import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from constants import flag_url


def render_group_stage_tab(sim):
    all_standings = sim['all_standings']

    col_select, _ = st.columns([2, 5])
    with col_select:
        group_letter = st.selectbox("Group", sorted(all_standings.keys()), label_visibility="collapsed")

    standings = all_standings[group_letter]

    st.markdown(f"<div style='font-size:11px; font-weight:600; letter-spacing:0.1em; text-transform:uppercase; color:rgba(255,255,255,0.25); margin:16px 0 10px 0;'>Group {group_letter}</div>", unsafe_allow_html=True)

    for rank, team_data in enumerate(standings, 1):
        team = team_data['team']
        pts = team_data['points']
        gf = team_data['goals_for']
        ga = team_data['goals_against']
        gd = team_data['goal_diff']

        if rank <= 2:
            border_color = "rgba(74,222,128,0.3)"
            rank_color = "#4ade80"
            bg = "rgba(74,222,128,0.04)"
        elif rank == 3:
            border_color = "rgba(250,204,21,0.3)"
            rank_color = "#facc15"
            bg = "rgba(250,204,21,0.04)"
        else:
            border_color = "rgba(255,255,255,0.06)"
            rank_color = "rgba(255,255,255,0.2)"
            bg = "rgba(255,255,255,0.01)"

        flag = flag_url(team)
        flag_html = f"<img src='{flag}' height='18' style='border-radius:2px; vertical-align:middle; margin-right:8px;'>" if flag else ""

        st.markdown(f"""
        <div style='display:flex; align-items:center; background:{bg};
                    border:1px solid {border_color}; border-radius:10px;
                    padding:12px 16px; margin-bottom:6px; gap:12px;'>
            <div style='font-size:13px; font-weight:700; color:{rank_color}; min-width:16px;'>{rank}</div>
            <div style='flex:1; font-size:14px; font-weight:500; color:#fff;'>{flag_html}{team}</div>
            <div style='display:flex; gap:20px; text-align:center;'>
                <div><div style='font-size:10px; color:rgba(255,255,255,0.25); text-transform:uppercase; letter-spacing:0.06em;'>P</div><div style='font-size:13px; color:rgba(255,255,255,0.6);'>3</div></div>
                <div><div style='font-size:10px; color:rgba(255,255,255,0.25); text-transform:uppercase; letter-spacing:0.06em;'>GF</div><div style='font-size:13px; color:rgba(255,255,255,0.6);'>{gf}</div></div>
                <div><div style='font-size:10px; color:rgba(255,255,255,0.25); text-transform:uppercase; letter-spacing:0.06em;'>GA</div><div style='font-size:13px; color:rgba(255,255,255,0.6);'>{ga}</div></div>
                <div><div style='font-size:10px; color:rgba(255,255,255,0.25); text-transform:uppercase; letter-spacing:0.06em;'>GD</div><div style='font-size:13px; color:rgba(255,255,255,0.6);'>{"+"+str(gd) if gd > 0 else str(gd)}</div></div>
                <div><div style='font-size:10px; color:rgba(255,255,255,0.25); text-transform:uppercase; letter-spacing:0.06em;'>Pts</div><div style='font-size:13px; font-weight:700; color:#fff;'>{pts}</div></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div style='margin-top:12px; font-size:11px; color:rgba(255,255,255,0.25); display:flex; gap:16px;'>
        <span><span style='color:rgba(74,222,128,0.7);'>●</span> 1st–2nd qualify automatically</span>
        <span><span style='color:rgba(250,204,21,0.7);'>●</span> 3rd may qualify as best third-placed team</span>
    </div>
    """, unsafe_allow_html=True)


def render_round_of_32_tab(sim):
    bracket = sim['bracket']

    st.markdown("""
    <div style='font-size:12px; color:rgba(255,255,255,0.3); margin-bottom:20px; line-height:1.6;'>
        16 matchups — pairings respect FIFA's no group-stage rematch rule.
    </div>
    """, unsafe_allow_html=True)

    cols_per_row = 4
    for row_start in range(0, len(bracket), cols_per_row):
        row_matches = bracket[row_start:row_start + cols_per_row]
        cols = st.columns(cols_per_row)

        for col, (team_a, team_b) in zip(cols, row_matches):
            match_num = bracket.index((team_a, team_b)) + 1
            url_a = flag_url(team_a)
            url_b = flag_url(team_b)
            flag_a = f"<img src='{url_a}' height='16' style='border-radius:2px; vertical-align:middle; margin-right:6px;'>" if url_a else ""
            flag_b = f"<img src='{url_b}' height='16' style='border-radius:2px; vertical-align:middle; margin-right:6px;'>" if url_b else ""

            with col:
                st.markdown(f"""
                <div style='background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.08);
                            border-radius:12px; padding:14px 16px; margin-bottom:8px;'>
                    <div style='font-size:10px; font-weight:600; letter-spacing:0.08em; text-transform:uppercase;
                                color:rgba(255,255,255,0.2); margin-bottom:10px;'>Match {match_num}</div>
                    <div style='font-size:13px; font-weight:500; color:#fff; margin-bottom:6px;'>{flag_a}{team_a}</div>
                    <div style='font-size:10px; color:rgba(255,255,255,0.2); margin-bottom:6px; padding-left:2px;'>vs</div>
                    <div style='font-size:13px; font-weight:500; color:#fff;'>{flag_b}{team_b}</div>
                </div>
                """, unsafe_allow_html=True)


def render_knockout_tab(sim):
    all_rounds = sim['all_rounds']
    champion = sim['champion']

    round_order = ['Round of 32', 'Round of 16', 'Quarter-finals', 'Semi-finals', 'Final']
    round_labels = ['Ro32', 'Ro16', 'QF', 'SF', 'Final']

    box_w = 190
    box_h = 54
    col_gap = 50
    row_gap = 10
    y_offset = 30
    label_h = 22
    total_width = len(round_order) * (box_w + col_gap) + 40

    section_height = 16 * (box_h + row_gap)
    svg_height = y_offset + label_h + section_height + 40

    parts = []

    for col_idx, (round_name, short) in enumerate(zip(round_order, round_labels)):
        results = all_rounds[round_name]
        n = len(results)
        spacing = section_height / n
        x = col_idx * (box_w + col_gap) + 20

        parts.append(f'<text x="{x + box_w/2}" y="{y_offset}" text-anchor="middle" font-size="11" font-weight="600" fill="rgba(255,255,255,0.25)" letter-spacing="1" style="text-transform:uppercase;">{short}</text>')

        for i, match in enumerate(results):
            y = y_offset + label_h + i * spacing + (spacing - box_h) / 2
            winner = match['winner']
            team_a = match['team_a']
            team_b = match['team_b']
            ga = match['goals_a']
            gb = match['goals_b']
            pen = "P" if match['penalties'] else ""

            a_win = winner == team_a
            b_win = winner == team_b

            a_fill = "#4ade80" if a_win else "rgba(255,255,255,0.3)"
            b_fill = "#4ade80" if b_win else "rgba(255,255,255,0.3)"
            a_weight = "600" if a_win else "400"
            b_weight = "600" if b_win else "400"

            score_a = f"{ga}{pen if a_win else ''}"
            score_b = f"{gb}{pen if b_win else ''}"

            mid_y = y + box_h / 2

            parts.append(f'''
<rect x="{x}" y="{y}" width="{box_w}" height="{box_h}" rx="8"
      fill="rgba(255,255,255,0.025)" stroke="rgba(255,255,255,0.08)" stroke-width="0.5"/>
<line x1="{x+8}" y1="{mid_y}" x2="{x+box_w-8}" y2="{mid_y}"
      stroke="rgba(255,255,255,0.06)" stroke-width="0.5"/>
<text x="{x+10}" y="{y+19}" font-size="11.5" fill="{a_fill}" font-weight="{a_weight}"
      font-family="sans-serif">{team_a[:20]}</text>
<text x="{x+box_w-8}" y="{y+19}" font-size="12" fill="{a_fill}" font-weight="700"
      text-anchor="end" font-family="sans-serif">{score_a}</text>
<text x="{x+10}" y="{y+42}" font-size="11.5" fill="{b_fill}" font-weight="{b_weight}"
      font-family="sans-serif">{team_b[:20]}</text>
<text x="{x+box_w-8}" y="{y+42}" font-size="12" fill="{b_fill}" font-weight="700"
      text-anchor="end" font-family="sans-serif">{score_b}</text>
''')

            if col_idx < len(round_order) - 1:
                next_n = len(all_rounds[round_order[col_idx + 1]])
                next_spacing = section_height / next_n
                match_in_next = i // 2
                next_y_top = y_offset + label_h + match_in_next * next_spacing
                next_mid_y = next_y_top + next_spacing / 2
                right_x = x + box_w
                next_left_x = x + box_w + col_gap

                parts.append(f'''
<polyline points="{right_x},{mid_y} {right_x + col_gap/2},{mid_y} {right_x + col_gap/2},{next_mid_y} {next_left_x},{next_mid_y}"
          fill="none" stroke="rgba(255,255,255,0.08)" stroke-width="1"/>
''')

    svg = f'''<svg width="100%" viewBox="0 0 {total_width} {svg_height}"
         xmlns="http://www.w3.org/2000/svg"
         style="font-family:sans-serif; background:transparent; display:block;">
    {''.join(parts)}
</svg>'''

    components.html(
        f'<div style="overflow-x:auto; overflow-y:hidden; background:transparent;">{svg}</div>',
        height=int(svg_height) + 40,
        scrolling=False
    )