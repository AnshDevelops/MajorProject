import gradio as gr

from .character_graph import (
    relations_graph,
    add_character,
    add_relation,
    delete_character,
    save,
    load,
)
from .events_graph import events_graph, add_plot, add_subplot, delete_plot
from .extractor import extract_entities, extract_events
from .image_gen import generate_images
from .traits import add_trait, delete_trait, character_traits


def build():
    with gr.Blocks(
        theme=gr.themes.Soft(primary_hue="blue", secondary_hue="cyan")
    ) as demo:
        gr.Markdown("## ✨ EpicFrame – Narrative Workbench")

        relations_state = gr.State({"characters": [], "relations": [], "traits": {}})
        events_state = gr.State({"plots": [], "subplots": []})

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

        with gr.Tab("Timeline"):
            with gr.Row():
                timeline_graph = gr.Image(
                    interactive=False,
                    show_label=False,
                    container=False,
                    scale=1,
                    min_width=800,
                    height=500,
                )
                plot_list = gr.JSON(
                    label="Available Plots",
                    show_label=True,
                    container=True,
                )

            with gr.Row():
                with gr.Column():
                    gr.Markdown("### Add Plot")
                    plot_event = gr.Textbox(label="Event Description")
                    plot_seq = gr.Number(
                        label="Sequence Number (optional)", precision=0
                    )
                    add_plot_btn = gr.Button("Add Plot")

                with gr.Column():
                    gr.Markdown("### Add Subplot Connection")
                    from_plot = gr.Dropdown(
                        label="From Plot", choices=[], allow_custom_value=False
                    )
                    to_plot = gr.Dropdown(
                        label="To Plot", choices=[], allow_custom_value=False
                    )
                    subplot_event = gr.Textbox(label="Connection Description")
                    add_subplot_btn = gr.Button("Add Connection")

                with gr.Column():
                    gr.Markdown("### Delete Plot")
                    del_plot_id = gr.Dropdown(
                        label="Select Plot to Delete",
                        choices=[],
                        allow_custom_value=False,
                    )
                    del_plot_btn = gr.Button("Delete Plot")

            timeline_msg = gr.Textbox(max_lines=2, label="Status")

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
        def generate_assets(prompt, style, q, num, rel_state, evt_state):
            char_data = extract_entities(prompt)
            event_data = extract_events(prompt)
            g_path = relations_graph(char_data)
            t_path = events_graph(event_data)
            imgs = generate_images(prompt, style, q, int(num)) if num else []
            msg = "✅ All assets generated." if imgs else "✅ Graphs generated."

            rel_state.update(char_data)
            evt_state.update(event_data)

            plot_list, plot_choices = get_plot_list(event_data)

            return (
                imgs,
                g_path,
                t_path,
                msg,
                rel_state,
                evt_state,
                gr.update(choices=char_data["characters"]),
                char_data.get("traits", {}),
                plot_list,
                gr.update(choices=plot_choices),
                gr.update(choices=plot_choices),
                gr.update(choices=plot_choices),
            )

        gen_btn.click(
            generate_assets,
            inputs=[story, style, quality, n_img, relations_state, events_state],
            outputs=[
                gallery,
                graph,
                timeline_graph,
                status,
                relations_state,
                events_state,
                char_sel,
                traits_view,
            ],
        )

        # ─────────── char / relation edits ────────────────────────
        add_char_btn.click(
            lambda n, s: (
                add_character(s, n),
                "",
                s,
                gr.update(choices=s["characters"]),
            ),
            inputs=[add_name, relations_state],
            outputs=[graph, tweak_msg, relations_state, char_sel],
        )
        add_rel_btn.click(
            lambda f, t, ty, s: (add_relation(s, f, t, ty), "", s),
            inputs=[frm, to, typ, relations_state],
            outputs=[graph, tweak_msg, relations_state],
        )
        del_char_btn.click(
            lambda n, s: (
                delete_character(s, n),
                "",
                s,
                gr.update(choices=s["characters"]),
                {},
            ),
            inputs=[del_name, relations_state],
            outputs=[graph, tweak_msg, relations_state, char_sel, traits_view],
        )

        # ─────────── trait edits ──────────────────────────────────
        def _show(c, s):
            return character_traits(s, c) if c else {}

        add_tr_btn.click(
            lambda c, k, v, s: (_show(c, add_trait(s, c, k, v)), s),
            inputs=[char_sel, trait_key, trait_val, relations_state],
            outputs=[traits_view, relations_state],
        )
        del_tr_btn.click(
            lambda c, k, s: (_show(c, delete_trait(s, c, k)), s),
            inputs=[char_sel, trait_key, relations_state],
            outputs=[traits_view, relations_state],
        )

        # ─────────── timeline edits ──────────────────────────────
        def get_plot_list(state):
            """Format plots for display and update dropdowns."""
            plot_list = [
                {"ID": p["id"], "Sequence": p["sequence"], "Event": p["event"]}
                for p in sorted(state["plots"], key=lambda x: x["sequence"])
            ]

            plot_choices = [p["id"] for p in state["plots"]]

            return plot_list, plot_choices

        def handle_plot_add(e, s, st):
            if not e:
                return (
                    gr.update(),
                    "Please enter an event description.",
                    st,
                    [],
                    gr.update(choices=[]),
                    gr.update(choices=[]),
                    gr.update(choices=[]),
                )

            t_path = add_plot(st, e, s)
            height = max(500, 100 * len(st["plots"]))
            plot_list, plot_choices = get_plot_list(st)

            return (
                gr.update(value=t_path, height=height),
                "✅ Plot added successfully.",
                st,
                plot_list,
                gr.update(choices=plot_choices),
                gr.update(choices=plot_choices),
                gr.update(choices=plot_choices),
            )

        def handle_subplot_add(f, t, e, st):
            if not all([f, t, e]):
                return (
                    gr.update(),
                    "Please fill in all subplot fields.",
                    st,
                    [],
                    gr.update(choices=[]),
                )

            if f == t:
                return (
                    gr.update(),
                    "Cannot connect a plot to itself.",
                    st,
                    [],
                    gr.update(choices=[]),
                )

            t_path = add_subplot(st, f, t, e)
            height = max(500, 100 * len(st["plots"]))
            plot_list, plot_choices = get_plot_list(st)

            return (
                gr.update(value=t_path, height=height),
                "✅ Connection added successfully.",
                st,
                plot_list,
                gr.update(choices=plot_choices),
            )

        def handle_plot_delete(i, st):
            if not i:
                return (
                    gr.update(),
                    "Please select a plot to delete.",
                    st,
                    [],
                    gr.update(choices=[]),
                    gr.update(choices=[]),
                    gr.update(choices=[]),
                )

            t_path = delete_plot(st, i)
            height = max(500, 100 * len(st["plots"]))
            plot_list, plot_choices = get_plot_list(st)

            return (
                gr.update(value=t_path, height=height),
                "✅ Plot deleted successfully.",
                st,
                plot_list,
                gr.update(choices=plot_choices),
                gr.update(choices=plot_choices),
                gr.update(choices=plot_choices),
            )

        add_plot_btn.click(
            handle_plot_add,
            inputs=[plot_event, plot_seq, events_state],
            outputs=[
                timeline_graph,
                timeline_msg,
                events_state,
                plot_list,
                from_plot,
                to_plot,
                del_plot_id,
            ],
        )

        add_subplot_btn.click(
            handle_subplot_add,
            inputs=[from_plot, to_plot, subplot_event, events_state],
            outputs=[
                timeline_graph,
                timeline_msg,
                events_state,
                plot_list,
                del_plot_id,
            ],
        )

        del_plot_btn.click(
            handle_plot_delete,
            inputs=[del_plot_id, events_state],
            outputs=[
                timeline_graph,
                timeline_msg,
                events_state,
                plot_list,
                from_plot,
                to_plot,
                del_plot_id,
            ],
        )
        # ─────────── save / load ──────────────────────────────────
        save_btn.click(
            lambda rs, es: save({"relations": rs, "events": es}),
            inputs=[relations_state, events_state],
            outputs=save_btn,
            api_name="download",
        ).then(lambda _: "✅ JSON ready.", outputs=save_msg)

        load_btn.click(
            lambda f, rs, es: (
                relations_graph(load(f.name)["relations"]),
                events_graph(load(f.name)["events"]),  # Add timeline graph
                "✅ File loaded.",
                load(f.name)["relations"],
                load(f.name)["events"],  # Add events state
                gr.update(choices=load(f.name)["relations"]["characters"]),
                load(f.name)["relations"].get("traits", {}),
            )
            if f
            else (None, None, "No file.", rs, es, gr.update(), {}),
            inputs=[file_in, relations_state, events_state],
            outputs=[
                graph,
                timeline_graph,
                save_msg,
                relations_state,
                events_state,
                char_sel,
                traits_view,
            ],
        )

    return demo
