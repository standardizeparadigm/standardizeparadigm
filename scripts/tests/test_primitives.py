# -*- coding: utf-8 -*-
"""Test các viên gạch: escape, rút gọn số, icon, CSS, defs, khung thẻ."""

import unittest

from helpers import SCRIPTS, assert_valid_svg  # noqa: F401

from svgkit import primitives
from svgkit.primitives import human, num
from svgkit.palette import get_palette


class TestEscaping(unittest.TestCase):
    def test_ampersand(self):
        self.assertEqual(primitives.esc("A & B"), "A &amp; B")

    def test_angle_brackets(self):
        self.assertEqual(primitives.esc("<b>"), "&lt;b&gt;")

    def test_quotes(self):
        self.assertEqual(primitives.esc('say "hi"'), "say &quot;hi&quot;")

    def test_vietnamese_untouched(self):
        text = "Học sinh lớp 7 · Kon Tum"
        self.assertEqual(primitives.esc(text), text)

    def test_non_string_input(self):
        self.assertEqual(primitives.esc(42), "42")


class TestHuman(unittest.TestCase):
    def test_small_numbers(self):
        self.assertEqual(primitives.human(0), "0")
        self.assertEqual(primitives.human(999), "999")

    def test_thousands(self):
        self.assertEqual(primitives.human(1000), "1k")
        self.assertEqual(primitives.human(1284), "1.3k")

    def test_millions(self):
        self.assertEqual(primitives.human(2400000), "2.4M")

    def test_bad_input(self):
        self.assertEqual(primitives.human(None), "-")
        self.assertEqual(primitives.human("abc"), "-")

    def test_num_strips_trailing_zeros(self):
        self.assertEqual(primitives.num(12.0), "12")
        self.assertEqual(primitives.num(12.50), "12.5")


class TestIcons(unittest.TestCase):
    def test_all_icons_render(self):
        for name in primitives.ICONS:
            markup = primitives.icon(name, 10, 10, "#ffffff")
            self.assertIn("<g transform=", markup)
            self.assertNotIn("None", markup)

    def test_unknown_icon_falls_back(self):
        markup = primitives.icon("khong-co", 0, 0, "#ffffff")
        self.assertIn("circle", markup)


class TestStyle(unittest.TestCase):
    def test_css_has_no_placeholders_left(self):
        css = primitives.css_block(get_palette("emerald"))
        self.assertNotIn("@ACCENT@", css)
        self.assertNotIn("@FONT@", css)
        self.assertIn("emerald", "emerald")  # sanity

    def test_css_colors_follow_theme(self):
        sky = primitives.css_block(get_palette("sky"))
        violet = primitives.css_block(get_palette("violet"))
        self.assertNotEqual(sky, violet)
        self.assertIn("#F3EBFF", violet)   # màu tiêu đề của theme violet

    def test_defs_complete(self):
        defs = primitives.defs_block(get_palette())
        for gradient in ("bg", "edge", "titleGrad", "accentGrad", "barGrad",
                         "halo", "glow"):
            self.assertIn('id="%s"' % gradient, defs)
        self.assertNotIn("@", defs)


class TestOpenSvg(unittest.TestCase):
    def test_open_svg_parses(self):
        parts = primitives.open_svg(get_palette(), 640, 258, "test card")
        parts.append("</svg>")
        assert_valid_svg(self, "\n".join(parts))

    def test_contains_clip_and_border(self):
        markup = "\n".join(primitives.open_svg(get_palette(), 640, 258, "x"))
        self.assertIn('id="cardBody"', markup)
        self.assertIn('stroke="url(#edge)"', markup)

    def test_top_edge_carries_a_travelling_light(self):
        markup = "\n".join(primitives.open_svg(get_palette(), 640, 258, "x"))
        self.assertIn('y="0.4"', markup)
        self.assertIn('class="sheen"', markup)

    def test_travelling_light_sits_inside_the_clip(self):
        # phải nằm giữa <g clip-path> ... </g>, nếu không sẽ tràn góc bo
        markup = "\n".join(primitives.open_svg(get_palette(), 640, 258, "x"))
        before, _, after = markup.partition('y="0.4"')
        self.assertGreater(before.count("<g clip-path"), before.count("</g>"))
        self.assertIn("</g>", after)




class TestSheen(unittest.TestCase):
    """Vệt sáng quét mép trên: trang trí, nhưng dễ vỡ khi đổi kích thước."""

    def test_uses_the_sheen_gradient_and_keyframes(self):
        svg = primitives.sheen(get_palette("sky"), 640, 258)
        self.assertIn("url(#sheenGrad)", svg)
        self.assertIn('class="sheen"', svg)

    def test_delay_can_be_negative(self):
        svg = primitives.sheen(get_palette("sky"), 640, 258, delay=-2.5)
        self.assertIn("-2.5s", svg)

    def test_opacity_is_carried_through(self):
        self.assertIn('opacity="0.3"',
                      primitives.sheen(get_palette("sky"), 640, 258, opacity=0.3))

    def test_clip_id_is_derived_from_size(self):
        # id phải khác nhau giữa hai thẻ cùng trang, nếu không cả hai dùng
        # chung một clip và vệt sáng của thẻ nhỏ tràn sang thẻ lớn.
        small = primitives.sheen(get_palette("sky"), 640, 258)
        large = primitives.sheen(get_palette("sky"), 1000, 280)
        self.assertNotEqual(small.split('"')[1], large.split('"')[1])

    def test_class_matches_the_keyframes(self):
        self.assertIn('class="sheen"', primitives.sheen(get_palette("sky"), 640, 258))


class TestHumanNumbers(unittest.TestCase):
    """`human()` là chỗ dễ làm sai dấu thập phân nhất."""

    def test_exactly_one_thousand(self):
        # Bỏ ".0" là chủ ý: "1k" đọc nhanh hơn "1.0k".
        self.assertEqual(human(1000), "1k")

    def test_nine_ninety_nine(self):
        self.assertEqual(human(999), "999")

    def test_one_million(self):
        self.assertEqual(human(1_000_000), "1M")

    def test_rounds_to_one_decimal(self):
        self.assertEqual(human(1234), "1.2k")

    def test_negative_is_kept(self):
        self.assertEqual(human(-15), "-15")

    def test_string_input_is_accepted(self):
        self.assertEqual(human("42"), "42")

    def test_garbage_becomes_a_dash(self):
        self.assertEqual(human(None), "-")
        self.assertEqual(human("abc"), "-")

    def test_just_under_a_million(self):
        self.assertEqual(human(999_999), "1000k")



class TestNum(unittest.TestCase):
    """`num()` đi vào toạ độ SVG — sai một số là lệch cả hình."""

    def test_integer_has_no_decimal_point(self):
        self.assertEqual(num(12), "12")

    def test_one_decimal_is_kept(self):
        self.assertEqual(num(12.5), "12.5")

    def test_trailing_zero_is_dropped(self):
        self.assertEqual(num(12.0), "12")

    def test_rounds_to_one_decimal(self):
        self.assertEqual(num(12.34), "12.3")

    def test_negative_keeps_the_sign(self):
        self.assertEqual(num(-3.5), "-3.5")

    def test_never_returns_a_bare_dot(self):
        for value in (0, 0.0, -0.04, 1000000):
            self.assertNotIn(".", num(value).rstrip("."), num(value))



class TestEscEdgeCases(unittest.TestCase):
    """`esc` bảo vệ XML — nhưng không được làm hỏng dấu tiếng Việt."""

    def test_ampersand_first_then_brackets(self):
        # Thứ tự sai sẽ biến "<" thành "&amp;lt;".
        self.assertEqual(primitives.esc("<a & b>"), "&lt;a &amp; b&gt;")

    def test_quotes_are_escaped_for_attributes(self):
        self.assertEqual(primitives.esc('say "hi"'), "say &quot;hi&quot;")

    def test_vietnamese_is_untouched(self):
        text = "Quảng Ngãi · ĐẠT"
        self.assertEqual(primitives.esc(text), text)

    def test_numbers_become_strings(self):
        self.assertEqual(primitives.esc(42), "42")

    def test_no_double_escaping_of_entities_text(self):
        # Chuỗi đã có sẵn "&amp;" sẽ thành "&amp;amp;" — chấp nhận được, vì
        # esc chỉ nhận văn bản thô, chưa từng qua esc.
        self.assertEqual(primitives.esc("&amp;"), "&amp;amp;")


class TestNumFormatting(unittest.TestCase):
    def test_trims_trailing_zeros(self):
        self.assertEqual(num(12.0), "12")
        self.assertEqual(num(12.5), "12.5")
        self.assertEqual(num(12.34), "12.3")

    def test_zero_and_negative(self):
        self.assertEqual(num(0), "0")
        self.assertEqual(num(-3.0), "-3")

    def test_never_emits_negative_zero(self):
        self.assertNotEqual(num(-0.04), "-0")


class TestHumanFormatting(unittest.TestCase):
    def test_small_numbers_stay_whole(self):
        self.assertEqual(human(0), "0")
        self.assertEqual(human(999), "999")

    def test_thousands_and_millions(self):
        self.assertEqual(human(1284), "1.3k")
        self.assertEqual(human(2400000), "2.4M")

    def test_round_numbers_drop_the_decimal(self):
        self.assertEqual(human(3000), "3k")

    def test_junk_becomes_a_dash(self):
        for junk in (None, "abc", "", [], {}):
            self.assertEqual(human(junk), "-", repr(junk))


if __name__ == "__main__":
    unittest.main()


class TestReducedMotion(unittest.TestCase):
    def test_css_disables_animation_when_requested(self):
        from svgkit import primitives

        self.assertIn("prefers-reduced-motion", primitives.CSS)
        self.assertIn("animation: none !important", primitives.CSS)

    def test_every_animated_class_is_covered(self):
        import re

        from svgkit import primitives

        block = primitives.CSS.split("prefers-reduced-motion")[1]
        declared = set(re.findall(r"^\s*\.(\w+)\s*\{ animation:", primitives.CSS, re.M))
        for name in declared:
            self.assertIn("." + name, block, "thiếu %s trong khối giảm chuyển động" % name)


class TestNumbers(unittest.TestCase):
    def test_human_small(self):
        from svgkit.primitives import human

        self.assertEqual(human(0), "0")
        self.assertEqual(human(7), "7")
        self.assertEqual(human(999), "999")

    def test_human_thousands(self):
        from svgkit.primitives import human

        self.assertEqual(human(1000), "1k")
        self.assertEqual(human(3476), "3.5k")
        self.assertEqual(human(12345), "12.3k")

    def test_human_millions(self):
        from svgkit.primitives import human

        self.assertEqual(human(1200000), "1.2M")

    def test_num_trims_float(self):
        from svgkit.primitives import num

        self.assertEqual(num(12.0), "12")
        self.assertEqual(num(12.345), "12.3")


class TestEscape(unittest.TestCase):
    def test_special_characters(self):
        from svgkit.primitives import esc

        self.assertEqual(primitives.esc("a & b"), "a &amp; b")
        self.assertEqual(primitives.esc("<b>"), "&lt;b&gt;")
        self.assertEqual(primitives.esc('nói "xin chào"'), "nói &quot;xin chào&quot;")

    def test_vietnamese_untouched(self):
        from svgkit.primitives import esc

        self.assertEqual(primitives.esc("Lập trình viên tự học"), "Lập trình viên tự học")

    def test_escaped_text_stays_parseable(self):
        from helpers import parse
        from svgkit.primitives import esc

        svg = ('<svg xmlns="http://www.w3.org/2000/svg"><text>%s</text></svg>'
               % esc('5 < 7 & "8" > 6'))
        dom = parse(svg)
        node = dom.getElementsByTagName("text")[0]
        self.assertIn("<", node.firstChild.data)


class TestNewCssTokens(unittest.TestCase):
    """Hai lớp CSS mới của vòng 4 phải có mặt và phải tắt được khi cần."""

    def setUp(self):
        self.css = primitives.CSS

    def test_spin_dot_definition(self):
        self.assertIn(".spinDot", self.css)
        self.assertIn("transform-box: fill-box", self.css)

    def test_dash_flow_definition(self):
        self.assertIn(".dashFlow", self.css)
        self.assertIn("@keyframes dashFlow", self.css)
        self.assertIn("stroke-dashoffset", self.css)

    def test_both_are_disabled_by_reduced_motion(self):
        block = self.css[self.css.index("prefers-reduced-motion"):]
        for token in (".spinDot", ".dashFlow"):
            self.assertIn(token, block, "%s chưa được tắt" % token)


class TestIconFallback(unittest.TestCase):
    def test_unknown_icon_falls_back_to_spark(self):
        from svgkit.primitives import ICONS, icon

        out = icon("khong-co-icon-nay", 0, 0, "#FFFFFF")
        self.assertIn(ICONS["spark"], out)
        self.assertIn("<g", out)

    def test_known_icons_draw_path(self):
        from svgkit.primitives import ICONS, icon

        for name in ICONS:
            out = icon(name, 10, 20, "#38BDF8")
            self.assertIn("<path", out, name)
            self.assertIn("#38BDF8", out, name)
