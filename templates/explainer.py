"""Template Manim project for a 7-9 minute geometric educational explainer.

Replace PLAN and Scene.construct implementations with source-specific content.
Keep PLAN as a literal list so build.py can statically export narration,
subtitles, chapters, and cue scripts without importing Manim.
"""
from __future__ import annotations

from manim import *
import numpy as np

# Dark geometric explainer palette.
BG = "#090E1A"
INK = "#EAF2FF"
MUTED = "#8B95A7"
GRID = "#253044"
BLUE = "#4EA3FF"
TEAL = "#2DD4BF"
YELLOW = "#FFD166"
RED = "#FF6B6B"
GREEN = "#8BD17C"

config.background_color = BG

PLAN = [
    {"scene": "Motivation", "title": "Why this matters", "duration": 70, "source": "Source: replace with paper/article section", "beats": [
        {"start": 0, "end": 18, "visual": "Introduce the real-world problem as one simple geometric object.", "text": "Start with the problem. Replace this narration with a concrete hook from the source material, stated in plain language."},
        {"start": 18, "end": 36, "visual": "Reveal why the naive solution fails.", "text": "Now show why the obvious approach is not enough. The animation should make the failure visible before naming it."},
        {"start": 36, "end": 54, "visual": "Morph the problem object into the central metaphor for the video.", "text": "The key is to choose a metaphor that can carry the whole explanation, rather than listing facts from the paper."},
        {"start": 54, "end": 70, "visual": "Preview the path: problem, insight, mechanism, evidence, takeaway.", "text": "By the end, the viewer should understand the main idea, what it buys us, and where its limits are."},
    ]},
    {"scene": "KeyInsight", "title": "The key insight", "duration": 80, "source": "Source: replace with core method/argument", "beats": [
        {"start": 0, "end": 20, "visual": "Two representations appear side by side and begin to align.", "text": "Here is the central insight. Replace this cue with the paper's conceptual move, not its implementation details."},
        {"start": 20, "end": 40, "visual": "A yellow bridge or transformation connects the two views.", "text": "Use the animation to show how one view turns into another. Let the diagram do most of the explaining."},
        {"start": 40, "end": 60, "visual": "Add the first compact equation or rule if helpful.", "text": "If there is an equation, introduce it term by term. Every symbol should correspond to something already visible."},
        {"start": 60, "end": 80, "visual": "Summarize the insight as a reusable visual rule.", "text": "The result is a mental model the viewer can carry into the mechanism section."},
    ]},
    {"scene": "Mechanism", "title": "How it works", "duration": 120, "source": "Source: replace with method section", "beats": [
        {"start": 0, "end": 24, "visual": "Build the mechanism from simple blocks.", "text": "Now we open the box. Start with the smallest moving part, and avoid naming every component at once."},
        {"start": 24, "end": 48, "visual": "Animate one input passing through the mechanism.", "text": "Follow a single example through the system. This keeps the viewer oriented while the diagram grows."},
        {"start": 48, "end": 72, "visual": "Reveal a branching or selection step.", "text": "When the method makes a choice, show the alternatives first, then reveal the selected path."},
        {"start": 72, "end": 96, "visual": "Combine intermediate pieces into an output.", "text": "The output should feel like a consequence of the previous transformations, not a new fact dropped on screen."},
        {"start": 96, "end": 120, "visual": "Condense the mechanism into a compact schematic.", "text": "End this section with a diagram simple enough to reuse in the rest of the video."},
    ]},
    {"scene": "WhyItMatters", "title": "Why the constraint matters", "duration": 100, "source": "Source: replace with loss/regularization/caveat/limitation", "beats": [
        {"start": 0, "end": 20, "visual": "Show the mechanism failing in an exaggerated toy case.", "text": "Most good methods include a counterweight. First, make the failure mode visible in a toy version."},
        {"start": 20, "end": 45, "visual": "Introduce the regularizer, constraint, or caveat as a balancing force.", "text": "Then introduce the constraint as a force that changes behavior, not merely as an extra term in a formula."},
        {"start": 45, "end": 70, "visual": "Compare before and after side by side.", "text": "A side by side comparison is often more intuitive than a paragraph of explanation."},
        {"start": 70, "end": 100, "visual": "Connect the toy picture back to the real claim.", "text": "Finally, reconnect the toy picture to the source. Be explicit about what is measured and what is illustrative."},
    ]},
    {"scene": "Evidence", "title": "What the evidence says", "duration": 90, "source": "Source: replace with experiments/results", "beats": [
        {"start": 0, "end": 18, "visual": "Introduce the dataset or evidence source as simple icons/cards.", "text": "Now we ask what evidence the source gives. Start by showing where the numbers come from."},
        {"start": 18, "end": 42, "visual": "Build a chart with the most important comparison.", "text": "Choose the comparison that best supports the central story. Do not overload the screen with every metric."},
        {"start": 42, "end": 66, "visual": "Add caveats, uncertainty, or generalization gap visibly.", "text": "Good explanation includes the boundary of the claim. Show what the result does not prove."},
        {"start": 66, "end": 90, "visual": "Collapse results into one takeaway chart or table.", "text": "The takeaway should be accurate, memorable, and more modest than the strongest possible marketing claim."},
    ]},
    {"scene": "Takeaway", "title": "Takeaway", "duration": 60, "source": "Source: replace with conclusion/implications", "beats": [
        {"start": 0, "end": 18, "visual": "Return to the opening metaphor.", "text": "Return to the first image. The viewer should now see it differently."},
        {"start": 18, "end": 36, "visual": "Reconnect problem, insight, mechanism, and evidence.", "text": "Summarize the chain: the problem, the key idea, how the method works, and why the constraint matters."},
        {"start": 36, "end": 50, "visual": "Show the practical implication or next question.", "text": "End with what this lets us do, or what question it opens next."},
        {"start": 50, "end": 60, "visual": "Final clean title card.", "text": "Leave the viewer with one sentence they could explain to someone else."},
    ]},
]


def text(s: str, size: float = 30, color: str = INK, width: float | None = None) -> Text:
    t = Text(s, font="Helvetica Neue", font_size=size, color=color)
    if width and t.width > width:
        t.scale_to_fit_width(width)
    return t


def box(label: str, width: float = 3.0, height: float = 0.8, color: str = BLUE) -> VGroup:
    rect = RoundedRectangle(width=width, height=height, corner_radius=0.12,
                            color=color, stroke_width=2, fill_color=color, fill_opacity=0.08)
    lab = text(label, 24, INK, width=width - 0.25).move_to(rect)
    return VGroup(rect, lab)


def math_tex(*parts: str, size: float = 42) -> MathTex:
    m = MathTex(*parts, font_size=size, color=INK)
    if m.width > 12.5:
        m.scale_to_fit_width(12.5)
    return m


class TimedScene(Scene):
    def setup(self):
        self.spec = next(p for p in PLAN if p["scene"] == self.__class__.__name__)
        self.clock = 0.0
        self.current_beat = 0
        self.hud = None

    def go(self, *animations: Animation, seconds: float = 1.0, rate_func=smooth):
        self.play(*animations, run_time=seconds, rate_func=rate_func)
        self.clock = round(self.clock + seconds, 6)

    def hold(self, seconds: float):
        if seconds > 1e-6:
            self.wait(seconds)
            self.clock = round(self.clock + seconds, 6)

    def at(self, seconds: float):
        if self.clock > seconds + 0.035:
            raise RuntimeError(f"{self.__class__.__name__}: timing overrun {self.clock:.3f} > {seconds:.3f}")
        self.hold(max(0.0, seconds - self.clock))

    def beat(self, index: int):
        self.current_beat = index
        self.at(self.spec["beats"][index]["start"])

    def within(self, seconds: float):
        self.at(self.spec["beats"][self.current_beat]["start"] + seconds)

    def heading(self):
        n = next(i for i, p in enumerate(PLAN, 1) if p is self.spec)
        tag = text(f"{n:02d} / EXPLAINER", 14, TEAL).to_corner(UL, buff=0.38)
        title = text(self.spec["title"], 34, width=12.6)
        title.to_edge(LEFT, buff=0.50).set_y(3.16)
        rule = Line([-6.6, 2.77, 0], [6.6, 2.77, 0], color=GRID, stroke_width=1)
        footer = text(self.spec["source"], 13, MUTED, width=12.8).to_edge(LEFT, buff=0.50).set_y(-3.67)
        self.hud = VGroup(tag, title, rule, footer)
        self.go(FadeIn(self.hud), seconds=0.6)

    def finish(self):
        self.at(self.spec["duration"] - 0.8)
        for m in self.mobjects:
            m.clear_updaters(recursive=True)
        self.go(*[FadeOut(m) for m in list(self.mobjects)], seconds=0.8)
        assert abs(self.clock - self.spec["duration"]) < 1e-4


class Motivation(TimedScene):
    def construct(self):
        self.beat(0); self.heading()
        problem = box("Problem", 3.2, 0.9, BLUE).move_to([-3.2, 0.4, 0])
        question = text("What is hard here?", 34, YELLOW).move_to([2.2, 0.4, 0])
        self.go(GrowFromCenter(problem), Write(question), seconds=1.4)
        self.within(10); self.go(Indicate(problem, color=YELLOW), seconds=1.0)

        self.beat(1)
        naive = box("Naive answer", 3.4, 0.8, RED).move_to([0, -0.7, 0])
        cross = Cross(naive, stroke_color=RED, stroke_width=4)
        self.go(TransformFromCopy(problem, naive), seconds=1.2)
        self.go(Create(cross), seconds=0.8)

        self.beat(2)
        metaphor = VGroup(*[Circle(radius=0.34, color=c, fill_opacity=0.18).move_to([x, 0.7, 0])
                            for x, c in zip(np.linspace(-2.4, 2.4, 5), [BLUE, TEAL, YELLOW, TEAL, BLUE])])
        arrows = VGroup(*[Arrow(metaphor[i].get_right(), metaphor[i+1].get_left(), buff=0.08, color=GRID)
                          for i in range(4)])
        self.go(FadeOut(naive), FadeOut(cross), FadeOut(question), Transform(problem, box("Visual metaphor", 3.7, 0.9, TEAL).move_to([0, -1.2, 0])), seconds=1.0)
        self.go(FadeIn(metaphor), Create(arrows), seconds=1.6)

        self.beat(3)
        roadmap = VGroup(*[box(s, 2.2, 0.55, c) for s, c in [("problem", BLUE), ("insight", TEAL), ("mechanism", YELLOW), ("evidence", GREEN)]])
        roadmap.arrange(RIGHT, buff=0.25).move_to([0, 1.75, 0])
        self.go(FadeIn(roadmap, shift=UP * 0.2), seconds=1.2)
        self.finish()


class KeyInsight(TimedScene):
    def construct(self):
        self.beat(0); self.heading()
        left = box("Old view", 3.2, 1.0, BLUE).move_to([-3.2, 0.4, 0])
        right = box("New view", 3.2, 1.0, TEAL).move_to([3.2, 0.4, 0])
        self.go(FadeIn(left), FadeIn(right), seconds=1.2)
        self.beat(1)
        bridge = Arrow(left.get_right(), right.get_left(), buff=0.2, color=YELLOW, stroke_width=6)
        self.go(GrowArrow(bridge), seconds=1.3)
        self.beat(2)
        eq = math_tex(r"\text{old representation}", r"\rightarrow", r"\text{useful representation}", size=34).move_to([0, -1.3, 0])
        self.go(Write(eq), seconds=1.4)
        self.beat(3)
        rule = text("One visual rule to reuse", 34, YELLOW).move_to([0, 1.85, 0])
        self.go(FadeIn(rule), Indicate(bridge, color=YELLOW), seconds=1.2)
        self.finish()


class Mechanism(TimedScene):
    def construct(self):
        self.beat(0); self.heading()
        blocks = VGroup(*[box(s, 2.3, 0.75, c) for s, c in [("input", BLUE), ("transform", TEAL), ("output", YELLOW)]])
        blocks.arrange(RIGHT, buff=0.9).move_to([0, 0.2, 0])
        arrows = VGroup(*[Arrow(blocks[i].get_right(), blocks[i+1].get_left(), buff=0.12, color=GRID) for i in range(2)])
        self.go(FadeIn(blocks[0]), seconds=0.8)
        self.go(Create(arrows[0]), FadeIn(blocks[1]), Create(arrows[1]), FadeIn(blocks[2]), seconds=1.6)
        self.beat(1)
        dot = Dot(blocks[0].get_center(), color=YELLOW, radius=0.09)
        self.add(dot); self.go(dot.animate.move_to(blocks[1].get_center()), seconds=1.2); self.go(dot.animate.move_to(blocks[2].get_center()), seconds=1.2); self.remove(dot)
        self.beat(2)
        branches = VGroup(*[box(f"path {i}", 1.6, 0.55, TEAL).move_to([0.0, y, 0]) for i, y in enumerate([1.35, 0.55, -0.25], 1)])
        self.go(FadeIn(branches), seconds=1.2)
        self.go(Indicate(branches[1], color=YELLOW), seconds=1.0)
        self.beat(3)
        combined = box("combined result", 3.4, 0.8, GREEN).move_to([3.0, -1.35, 0])
        self.go(TransformFromCopy(branches, combined), seconds=1.3)
        self.beat(4)
        schematic = VGroup(blocks, arrows, branches, combined).copy().scale(0.58).to_edge(DOWN, buff=0.75)
        self.go(FadeOut(blocks), FadeOut(arrows), FadeOut(branches), FadeOut(combined), FadeIn(schematic), seconds=1.2)
        self.finish()


class WhyItMatters(TimedScene):
    def construct(self):
        self.beat(0); self.heading()
        bad = VGroup(*[Circle(0.16, color=YELLOW, fill_opacity=0.6).move_to([-3 + 0.16*i, 0.8*np.sin(i), 0]) for i in range(16)])
        trap = box("failure mode", 3.2, 1.0, RED).move_to([2.7, 0, 0])
        self.go(FadeIn(bad), FadeIn(trap), seconds=1.2)
        self.go(*[m.animate.move_to(trap.get_center() + 0.15*np.random.default_rng(i).normal(size=3)) for i, m in enumerate(bad)], seconds=1.6)
        self.beat(1)
        balance = math_tex(r"L", "=", r"L_{main}", "+", r"\lambda L_{balance}", size=42).move_to([0, -1.45, 0])
        balance[4].set_color(YELLOW)
        self.go(Write(balance), seconds=1.4)
        self.beat(2)
        before = box("before", 2.5, 0.8, RED).move_to([-2.4, 1.3, 0])
        after = box("after", 2.5, 0.8, GREEN).move_to([2.4, 1.3, 0])
        self.go(FadeIn(before), FadeIn(after), seconds=1.0)
        self.beat(3)
        caveat = text("Toy picture ≠ measured trace", 28, MUTED).move_to([0, -2.4, 0])
        self.go(FadeIn(caveat), seconds=1.0)
        self.finish()


class Evidence(TimedScene):
    def construct(self):
        self.beat(0); self.heading()
        cards = VGroup(*[box(f"source {i}", 1.8, 0.65, BLUE).move_to([-3.6 + 1.8*i, 1.5, 0]) for i in range(5)])
        self.go(FadeIn(cards, lag_ratio=0.1), seconds=1.3)
        self.beat(1)
        axes = Axes(x_range=[0, 3, 1], y_range=[0, 1, 0.25], x_length=5, y_length=2.6,
                    tips=False, axis_config={"color": GRID}).move_to([0, -0.4, 0])
        bars = VGroup(*[Rectangle(width=0.65, height=h, color=c, fill_opacity=0.75).align_to(axes.c2p(i+0.6, 0), DOWN).shift(UP*h/2)
                        for i, (h, c) in enumerate([(0.7, BLUE), (1.6, TEAL), (2.2, YELLOW)])])
        self.go(Create(axes), GrowFromEdge(bars, DOWN), seconds=1.5)
        self.beat(2)
        gap = DashedLine([-1.5, 1.0, 0], [2.5, 1.0, 0], color=RED)
        note = text("claim boundary", 26, RED).next_to(gap, UP)
        self.go(Create(gap), FadeIn(note), seconds=1.0)
        self.beat(3)
        takeaway = box("evidence-backed takeaway", 4.4, 0.8, GREEN).move_to([0, -2.35, 0])
        self.go(FadeIn(takeaway), seconds=1.0)
        self.finish()


class Takeaway(TimedScene):
    def construct(self):
        self.beat(0); self.heading()
        first = box("opening image", 3.4, 0.9, BLUE).move_to([0, 0.4, 0])
        self.go(FadeIn(first), seconds=1.0)
        self.beat(1)
        chain = VGroup(*[box(s, 2.0, 0.55, c) for s, c in [("problem", BLUE), ("insight", TEAL), ("method", YELLOW), ("evidence", GREEN)]])
        chain.arrange(RIGHT, buff=0.2).move_to([0, -1.0, 0])
        self.go(FadeIn(chain, lag_ratio=0.1), seconds=1.2)
        self.beat(2)
        question = text("What should we do next?", 34, YELLOW).move_to([0, 1.8, 0])
        self.go(Write(question), seconds=1.2)
        self.beat(3)
        final = text("Replace with the one-sentence takeaway.", 34, INK, width=10.5).move_to([0, 0, 0])
        self.go(FadeOut(first), FadeOut(chain), FadeOut(question), FadeIn(final), seconds=1.2)
        self.finish()
