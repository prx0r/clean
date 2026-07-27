"""
Manim port of our PIL visual language scenes.
Palette matches renderer.py: DARK, GOLD, CRIMSON, INK, MUTED.
"""
from manim import *

P = {
    "bg": "#0c0c0f",
    "gold": "#d0ac5b",
    "crimson": "#8d2c39",
    "ink": "#ebe7dc",
    "muted": "#918d84",
    "dark_blue": "#0c1119",
}

class SpandaHook(Scene):
    """Port of spanda_scenes.py s_hook — The Hidden Pulse"""
    def construct(self):
        self.camera.background_color = P["bg"]

        # Center bindu — pulsing crimson dot
        bindu = Dot(ORIGIN, color=P["crimson"], radius=0.08)
        bindu.set_opacity(0)
        self.play(bindu.animate.set_opacity(1), run_time=2)
        self.add(bindu)

        # Breathing pulse animation using a ValueTracker
        pulse = ValueTracker(0)

        def update_bindu(mob):
            r = 0.08 + 0.03 * np.sin(pulse.get_value() * 0.6)
            mob.set_width(r * 2)

        bindu.add_updater(update_bindu)
        self.play(pulse.animate.set_value(20), run_time=6, rate_func=linear)
        bindu.clear_updaters()

        # Expanding rings — one by one
        rings = VGroup()
        for i in range(4):
            ring = Circle(radius=0.3 + i * 0.25, color=P["gold"], stroke_width=1.5)
            ring.set_opacity(0)
            rings.add(ring)

        self.play(*[r.animate.set_opacity(0.15 - i * 0.03) for i, r in enumerate(rings)], run_time=3)
        self.wait(1)

        # Slow ring breathing
        for ring in rings:
            orig_r = ring.radius
            def make_updater(r, orig):
                def upd(m):
                    m.radius = orig + 0.04 * np.sin(pulse.get_value() * 0.5 + rings.index(r))
                return upd
            ring.add_updater(make_updater(ring, orig_r))

        self.play(pulse.animate.set_value(30), run_time=10, rate_func=linear)
        for ring in rings:
            ring.clear_updaters()

        # Sanskrit text reveal
        text = Text("स्पन्द", font="Noto Serif Devanagari", color=P["crimson"], font_size=72)
        text.move_to(ORIGIN)
        text.set_opacity(0)
        self.play(Write(text, run_time=2))
        self.wait(2)

        # Fade out
        self.play(
            *[FadeOut(m, run_time=2) for m in [bindu, rings, text]]
        )


class SpandaWheel(Scene):
    """Port of spanda_scenes.py s_wheel — Wheel of Powers"""
    def construct(self):
        self.camera.background_color = P["bg"]

        # Central dot
        center = Dot(ORIGIN, color=P["gold"], radius=0.06)
        self.play(FadeIn(center, run_time=1))

        # Three spokes radiating
        spokes = VGroup()
        for i in range(3):
            angle = i * 2 * np.pi / 3
            end = np.array([np.cos(angle) * 1.5, np.sin(angle) * 1.5, 0])
            line = Line(ORIGIN, end, color=P["crimson"], stroke_width=2)
            spokes.add(line)

        # Outer rim
        rim = Circle(radius=1.6, color=P["gold"], stroke_width=2)

        self.play(
            Create(spokes, run_time=2),
            Create(rim, run_time=2),
        )
        self.wait(1)

        # Sanskrit verse
        verse = Text("यस्योन्मेषनिमेषाभ्यां जगतः प्रलयोदयौ",
                     font="Noto Serif Devanagari", color=P["gold"], font_size=36)
        verse.move_to(UP * 2)

        self.play(Write(verse, run_time=2))
        self.wait(2)

        # Slow rotation
        self.play(Rotate(VGroup(center, spokes, rim), angle=PI / 4, run_time=4))
        self.wait(1)

        # Fade
        self.play(*[FadeOut(m, run_time=2) for m in [center, spokes, rim, verse]])


class SpandaSixNames(Scene):
    """Port of spanda_scenes.py s_six — Six Names for One Thing"""
    def construct(self):
        self.camera.background_color = P["bg"]

        # Center dot
        center = Dot(ORIGIN, color=P["crimson"], radius=0.06)
        self.play(FadeIn(center))

        # Six names radiating
        names = [
            ("प्राणना", "vitality"),
            ("स्फुरत्ता", "effulgence"),
            ("विश्रान्ति", "repose"),
            ("जीव", "being"),
            ("हृदय", "heart"),
            ("स्पन्द", "vibration"),
        ]

        elements = VGroup()
        for i, (skt, eng) in enumerate(names):
            angle = i * 2 * np.pi / 6 - np.pi / 2
            x = np.cos(angle) * 2.0
            y = np.sin(angle) * 2.0

            # Small dot at each position
            dot = Dot(np.array([x, y, 0]), color=P["gold"], radius=0.04)

            # Sanskrit term
            skt_text = Text(skt, font="Noto Serif Devanagari", color=P["gold"], font_size=32)
            skt_text.move_to(np.array([x - 0.3, y + 0.3, 0]))

            # English translation
            eng_text = Text(eng, font="Sans", color=P["muted"], font_size=18)
            eng_text.move_to(np.array([x + 0.5, y - 0.2, 0]))

            # Connecting line
            line = Line(ORIGIN, np.array([x, y, 0]), color=P["gold_dim"], stroke_width=1)

            elements.add(dot, skt_text, eng_text, line)

            self.play(
                Create(line, run_time=0.5),
                FadeIn(dot, run_time=0.5),
                Write(skt_text, run_time=0.8),
                Write(eng_text, run_time=0.5),
            )

        # Title
        title = Text("six names for one thing", font="Sans", color=P["ink"], font_size=28)
        title.move_to(DOWN * 2.5)
        self.play(Write(title, run_time=1.5))
        self.wait(2)

        self.play(*[FadeOut(m, run_time=1.5) for m in [center, elements, title]])


class SpandaRecognition(Scene):
    """Port of spanda_scenes.py s_recog — Recognition / Mirror"""
    def construct(self):
        self.camera.background_color = P["bg"]

        # Vertical axis line
        axis = Line(UP * 3, DOWN * 3, color=P["muted"], stroke_width=1)
        self.play(Create(axis, run_time=1))

        # Particles converging to center
        dots = VGroup()
        for i in range(14):
            angle = i * 2 * np.pi / 14
            r = 2.4
            pos = np.array([np.cos(angle) * r, np.sin(angle) * r, 0])
            d = Dot(pos, color=P["gold"], radius=0.03)
            dots.add(d)

        self.play(FadeIn(dots, run_time=2))

        # Animate particles converging to center
        self.play(
            *[d.animate.move_to(ORIGIN + np.random.uniform(-0.1, 0.1, 3)) for d in dots],
            run_time=6,
            rate_func=there_and_back
        )
        self.wait(1)

        # Crimson center
        center = Dot(ORIGIN, color=P["crimson"], radius=0.1)
        self.play(FadeIn(center, run_time=1))
        self.wait(2)

        self.play(*[FadeOut(m, run_time=2) for m in [axis, dots, center]])
