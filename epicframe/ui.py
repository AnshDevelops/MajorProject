import gradio as gr
from .extractor import extract_entities
from .image_gen import generate_images
from .graph import (
    graph_png, add_character, add_relation, delete_character,
    save, load,
)
from .traits import add_trait, delete_trait, character_traits


def build():
    with gr.Blocks(theme=gr.themes.Soft(primary_hue="blue", secondary_hue="cyan")) as demo:
        gr.Markdown("## ✨ EpicFrame – Narrative Workbench")

        state = gr.State({"characters": [], "relations": [], "traits": {}})

        with gr.Tab("Input"):
            story = gr.Textbox(lines=6, label="Story prompt")
            style = gr.Dropdown(["Realistic", "Anime", "Sketch"], value="Realistic")
            quality = gr.Slider(1, 10, value=7, step=1, label="Image Quality")
            n_img = gr.Slider(0, 4, value=0, step=1, label="Images to generate")
            gen_btn = gr.Button("▶ Generate Assets")
            status = gr.Textbox(lines=2, label="Status")

        with gr.Tab("Images"):
            gallery = gr.Gallery(columns=4)

        with gr.Tab("Graph / Edit"):
            graph = gr.Image(interactive=False, height=500)
            add_name = gr.Textbox(label="Add Character → Name")
            add_char_btn = gr.Button("Add")
            frm = gr.Textbox(label="Relation From")
            to = gr.Textbox(label="To")
            typ = gr.Textbox(label="Type")
            add_rel_btn = gr.Button("Add Relation")
            del_name = gr.Textbox(label="Delete Character → Name")
            del_char_btn = gr.Button("Delete")
            tweak_msg = gr.Textbox(max_lines=2, label="➰ Status")

        with gr.Tab("Traits / Attributes"):
            char_sel = gr.Dropdown(label="Character")
            trait_key = gr.Textbox(label="Trait")
            trait_val = gr.Textbox(label="Value")
            add_tr_btn = gr.Button("Add / Update")
            del_tr_btn = gr.Button("Delete Trait")
            traits_view = gr.JSON(label="Current Traits")

        with gr.Tab("Save / Load"):
            save_btn = gr.Button("💾 Download JSON")
            file_in = gr.File(label="Load JSON")
            load_btn = gr.Button("⤵ Load")
            save_msg = gr.Textbox(max_lines=2, label="Status")

        # ─────────── core generate ────────────────────────────────
        def generate_assets(prompt, style, q, num, _old):
            data = extract_entities(prompt)
            g_path = graph_png(data)
            imgs = generate_images(prompt, style, q, int(num)) if num else []
            msg = "✅ All assets generated." if imgs else "✅ Graph generated."
            return (
                imgs,
                g_path,
                msg,
                data,  # new state
                gr.update(choices=data["characters"]),
                data.get("traits", {}),
            )

        gen_btn.click(
            generate_assets,
            inputs=[story, style, quality, n_img, state],
            outputs=[gallery, graph, status, state, char_sel, traits_view],
        )

        # ─────────── char / relation edits ────────────────────────
        add_char_btn.click(
            lambda n, s: (add_character(s, n), "", s, gr.update(choices=s["characters"])),
            inputs=[add_name, state],
            outputs=[graph, tweak_msg, state, char_sel],
        )
        add_rel_btn.click(
            lambda f, t, ty, s: (add_relation(s, f, t, ty), "", s),
            inputs=[frm, to, typ, state],
            outputs=[graph, tweak_msg, state],
        )
        del_char_btn.click(
            lambda n, s: (
                delete_character(s, n),
                "",
                s,
                gr.update(choices=s["characters"]),
                {},
            ),
            inputs=[del_name, state],
            outputs=[graph, tweak_msg, state, char_sel, traits_view],
        )

        # ─────────── trait edits ──────────────────────────────────
        def _show(c, s): return character_traits(s, c) if c else {}

        add_tr_btn.click(
            lambda c, k, v, s: (_show(c, add_trait(s, c, k, v)), s),
            inputs=[char_sel, trait_key, trait_val, state],
            outputs=[traits_view, state],
        )
        del_tr_btn.click(
            lambda c, k, s: (_show(c, delete_trait(s, c, k)), s),
            inputs=[char_sel, trait_key, state],
            outputs=[traits_view, state],
        )

        # ─────────── save / load ──────────────────────────────────
        save_btn.click(lambda s: save(s),
                       inputs=state, outputs=save_btn, api_name="download") \
            .then(lambda _: "✅ JSON ready.", outputs=save_msg)

        load_btn.click(
            lambda f, s: (
                graph_png(load(f.name)),
                "✅ File loaded.",
                load(f.name),
                gr.update(choices=load(f.name)["characters"]),
                load(f.name).get("traits", {}),
            ) if f else (None, "No file.", s, gr.update(), {}),
            inputs=[file_in, state],
            outputs=[graph, save_msg, state, char_sel, traits_view],
        )

    return demo
