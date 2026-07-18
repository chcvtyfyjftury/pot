"""بيانات ألعاب وأحداث Adjust الثابتة (مطابقة للبوت المرجعي بالكامل).

كل الألعاب والتوكنات والأحداث محفوظة هنا في الكود بدلاً من قاعدة البيانات،
بحيث تعمل منصة Adjust بشكل مطابق تماماً للبوت المرجعي.
"""

# (name, display_name, app_token, emoji)
ADJ_GAMES = [
    ("get_color", "🎨 Get Color", "367kicwptj5s", "🎨"),
    ("merge_blocks", "🔲 2048 X2 Merge Blocks", "367kicwptj5s", "🔲"),
    ("puzzle2248", "🧩 2248 Puzzle", "367kicwptj5s", "🧩"),
    ("alice_blastland", "🌸 Alice in Blastland", "367kicwptj5s", "🌸"),
    ("army_tycoon", "🎖️ Army Tycoon", "367kicwptj5s", "🎖️"),
    ("battle_night", "⚔️ Battle Night", "367kicwptj5s", "⚔️"),
    ("berry_factory", "🍓 Berry Factory Tycoon", "367kicwptj5s", "🍓"),
    ("big_card_solitaire", "🃏 Big Card Solitaire", "367kicwptj5s", "🃏"),
    ("bingo_aloha", "🍍 Bingo Aloha", "367kicwptj5s", "🍍"),
    ("bingo_showdown", "🎯 Bingo Showdown", "367kicwptj5s", "🎯"),
    ("blast_friends", "💥 Blast Friends", "367kicwptj5s", "💥"),
    ("block_blitz", "🧱 Block Blitz", "367kicwptj5s", "🧱"),
    ("block_joy", "🎮 Block Joy Puzzle", "367kicwptj5s", "🎮"),
    ("gems_adventure", "💎 Gems Adventure", "367kicwptj5s", "💎"),
    ("bravo_slots", "🎰 Bravo Classic Slots", "367kicwptj5s", "🎰"),
    ("cash_storm", "🌪️ Cash Storm", "367kicwptj5s", "🌪️"),
    ("climb_mountain", "⛰️ Climb the Mountain", "367kicwptj5s", "⛰️"),
    ("clock_maker", "⏰ Clock Maker", "367kicwptj5s", "⏰"),
    ("clone_evolution", "🧬 Clone Evolution", "367kicwptj5s", "🧬"),
    ("clubbillion", "🎲 Clubbillion Vegas", "367kicwptj5s", "🎲"),
    ("color_water_sort", "🎨 Color Water Sort", "367kicwptj5s", "🎨"),
    ("hot_rolls_dice", "🎲 Hot Rolls Dice", "8vvkgcwt0ykg", "🎲"),
]

# (game_name, event_name, event_token, display_name, level_value)
ADJ_EVENTS = [
    # Get Color
    ("get_color", "level_15", "8t8nb3", "🏆 Level 15", 15),
    ("get_color", "level_30", "uwq9v8", "🏆 Level 30", 30),
    ("get_color", "level_50", "fdlgyk", "🏆 Level 50", 50),
    ("get_color", "level_75", "dwhyjz", "🏆 Level 75", 75),
    ("get_color", "level_80", "34vgez", "🏆 Level 80", 80),
    ("get_color", "level_100", "txq8if", "🏆 Level 100", 100),
    ("get_color", "level_120", "lwhvaj", "🏆 Level 120", 120),
    ("get_color", "level_150", "iatv2g", "🏆 Level 150", 150),
    ("get_color", "level_200", "stpy1k", "🏆 Level 200", 200),
    ("get_color", "level_300", "53lena", "🏆 Level 300", 300),
    ("get_color", "level_400", "dbdy8l", "🏆 Level 400", 400),
    ("get_color", "level_500", "3i4yf5", "🏆 Level 500", 500),
    ("get_color", "level_700", "pwd51u", "🏆 Level 700", 700),
    ("get_color", "level_1000", "4o9jbt", "🏆 Level 1000", 1000),

    # 2048 X2 Merge Blocks
    ("merge_blocks", "event_callback_yd6777", "yd6777", "Reach step 5", 5),
    ("merge_blocks", "event_callback_8mpa1x", "8mpa1x", "Step 10", 10),
    ("merge_blocks", "event_callback_j9tstz", "j9tstz", "Step 25", 25),
    ("merge_blocks", "event_callback_g3mipt", "g3mipt", "Step 50", 50),
    ("merge_blocks", "event_callback_v197np", "v197np", "Step 100", 100),
    ("merge_blocks", "event_callback_vbwc0z", "vbwc0z", "Step 250", 250),
    ("merge_blocks", "event_callback_j7pzey", "j7pzey", "Step 500", 500),
    ("merge_blocks", "event_callback_47euyf", "47euyf", "Step 1000", 1000),
    ("merge_blocks", "event_callback_jom3es", "jom3es", "Make a purchase", 0),
    ("merge_blocks", "event_callback_2i73t2", "2i73t2", "Purchase", 0),

    # 2248 Puzzle
    ("puzzle2248", "event_callback_lumf2i", "lumf2i", "Level 10", 10),
    ("puzzle2248", "event_callback_p08k2f", "p08k2f", "Level 25", 25),
    ("puzzle2248", "event_callback_cciiv6", "cciiv6", "Level 50", 50),
    ("puzzle2248", "event_callback_yysyts", "yysyts", "Level 100", 100),
    ("puzzle2248", "event_callback_dhwefa", "dhwefa", "Level 250", 250),
    ("puzzle2248", "event_callback_hn8yew", "hn8yew", "Level 500", 500),
    ("puzzle2248", "event_callback_igqmwt", "igqmwt", "Level 1000", 1000),
    ("puzzle2248", "event_callback_236tr52", "236tr52", "Session", 0),

    # Alice in Blastland
    ("alice_blastland", "event_callback_uefzz6", "uefzz6", "Reach Level 5", 5),
    ("alice_blastland", "event_callback_15h2c4", "15h2c4", "Level 15", 15),
    ("alice_blastland", "event_callback_x2o8is", "x2o8is", "First time deposit", 0),
    ("alice_blastland", "event_callback_dndphq", "dndphq", "Reach Level 30", 30),
    ("alice_blastland", "event_callback_5oolhi", "5oolhi", "Reach Level 50", 50),
    ("alice_blastland", "event_callback_l5p54c", "l5p54c", "Reach Level 100", 100),
    ("alice_blastland", "event_callback_yhj1lm", "yhj1lm", "Level 200", 200),
    ("alice_blastland", "event_callback_i4juxt", "i4juxt", "Level 300", 300),
    ("alice_blastland", "event_callback_oftnes", "oftnes", "Level 500", 500),
    ("alice_blastland", "event_callback_z8ovou", "z8ovou", "Level 750", 750),
    ("alice_blastland", "event_callback_qww7m6", "qww7m6", "Level 1000", 1000),
    ("alice_blastland", "event_callback_25764", "25764", "Session", 0),

    # Army Tycoon
    ("army_tycoon", "event_callback_ucfrab", "ucfrab", "Unlock Artillery Course", 1),
    ("army_tycoon", "event_callback_kcii8f", "kcii8f", "Unlock Tank Course", 2),
    ("army_tycoon", "event_callback_1tgiij", "1tgiij", "Unlock Indoor Shooting Range", 3),
    ("army_tycoon", "event_callback_x2b508", "x2b508", "Unlock Helicopter Course", 4),
    ("army_tycoon", "event_callback_afpgpn", "afpgpn", "Event", 5),
    ("army_tycoon", "event_callback_24260", "24260", "Session", 0),

    # Battle Night
    ("battle_night", "event_callback_wdu1px", "wdu1px", "Collect 2 Purple Heroes", 2),
    ("battle_night", "event_callback_at7h8t", "at7h8t", "Purchase Month Card", 0),
    ("battle_night", "event_callback_f6z6gr", "f6z6gr", "Complete Chapter 6", 6),
    ("battle_night", "event_callback_8no4ma", "8no4ma", "Buy Login Premium Pass", 0),
    ("battle_night", "event_callback_jb6urh", "jb6urh", "Collect 1 Orange Hero", 1),
    ("battle_night", "event_callback_lltjkz", "lltjkz", "2 Orange Hero", 2),
    ("battle_night", "event_callback_9dy8xg", "9dy8xg", "4 Orange Hero", 4),
    ("battle_night", "event_callback_z8vm09", "z8vm09", "6 Orange Hero", 6),
    ("battle_night", "event_callback_98bp74", "98bp74", "9 Orange Hero", 9),
    ("battle_night", "event_callback_9aqu0l", "9aqu0l", "Reach VIP Level 4", 4),
    ("battle_night", "event_callback_36w4u0", "36w4u0", "12 Orange Hero", 12),
    ("battle_night", "event_callback_xjcc3q", "xjcc3q", "15 Orange Hero", 15),
    ("battle_night", "event_callback_4g2o7u", "4g2o7u", "1 Red Hero", 1),

    # Berry Factory
    ("berry_factory", "event_callback_vex04j", "vex04j", "Reach Dessert Factory", 1),
    ("berry_factory", "event_callback_f28p6w", "f28p6w", "Reach Candy Combine", 2),
    ("berry_factory", "event_callback_rsrv4q", "rsrv4q", "Reach Jelly Concern", 3),
    ("berry_factory", "event_callback_rktc9a", "rktc9a", "Upgrade Glazer to Maximum", 4),
    ("berry_factory", "event_callback_32t74", "32t74", "Session", 0),

    # Big Card Solitaire
    ("big_card_solitaire", "event_callback_y0oh58", "y0oh58", "First Time Deposit", 0),
    ("big_card_solitaire", "event_callback_58fm8f", "58fm8f", "Reach Level 15", 15),
    ("big_card_solitaire", "event_callback_iecaaf", "iecaaf", "Level 20", 20),
    ("big_card_solitaire", "event_callback_i31lvg", "i31lvg", "Level 30", 30),
    ("big_card_solitaire", "event_callback_vjrg9q", "vjrg9q", "Collect 3K Coins", 3000),
    ("big_card_solitaire", "event_callback_1fiiml", "1fiiml", "Collect 5K Coins", 5000),
    ("big_card_solitaire", "event_callback_rbxsf1", "rbxsf1", "Collect 7K Coins", 7000),
    ("big_card_solitaire", "event_callback_i4avja", "i4avja", "10K Coins", 10000),
    ("big_card_solitaire", "event_callback_j2y6j9", "j2y6j9", "20K Coins", 20000),
    ("big_card_solitaire", "event_callback_r5um2u", "r5um2u", "50K Coins", 50000),
    ("big_card_solitaire", "event_callback_bbyp36", "bbyp36", "100K Coins", 100000),
    ("big_card_solitaire", "event_callback_b8gfs7", "b8gfs7", "200K Coins", 200000),
    ("big_card_solitaire", "event_callback_rb2zo3", "rb2zo3", "400K Coins", 400000),

    # Bingo Aloha
    ("bingo_aloha", "event_callback_tr4vq2", "tr4vq2", "Reach Level 20", 20),
    ("bingo_aloha", "event_callback_f82iiq", "f82iiq", "Level 30", 30),
    ("bingo_aloha", "event_callback_ifxzih", "ifxzih", "Level 40", 40),
    ("bingo_aloha", "event_callback_3yza9s", "3yza9s", "Level 50", 50),
    ("bingo_aloha", "event_callback_pk6qyf", "pk6qyf", "Bonus: Level 60 within 3 days", 60),
    ("bingo_aloha", "event_callback_w5tltt", "w5tltt", "Level 80", 80),
    ("bingo_aloha", "event_callback_189lri", "189lri", "Level 120", 120),
    ("bingo_aloha", "event_callback_3g5fjn", "3g5fjn", "Level 150", 150),
    ("bingo_aloha", "event_callback_2vj74s", "2vj74s", "Bonus: Level 200 within 6 days", 200),
    ("bingo_aloha", "event_callback_ccm57s", "ccm57s", "Level 300", 300),
    ("bingo_aloha", "event_callback_pxvvbe", "pxvvbe", "Level 400", 400),
    ("bingo_aloha", "event_callback_uqst83", "uqst83", "Level 500", 500),
    ("bingo_aloha", "event_callback_3wfbqv", "3wfbqv", "Purchase $19.9", 0),
    ("bingo_aloha", "event_callback_ckugaz", "ckugaz", "Purchase $9.99", 0),
    ("bingo_aloha", "event_callback_uvz4f0", "uvz4f0", "Purchase $4.99", 0),

    # Bingo Showdown
    ("bingo_showdown", "event_callback_w10qxm", "w10qxm", "First Bingo", 1),
    ("bingo_showdown", "event_callback_3jdb4n", "3jdb4n", "Reach Level 2", 2),
    ("bingo_showdown", "event_callback_njnr15", "njnr15", "Level 3", 3),
    ("bingo_showdown", "event_callback_2sv8qt", "2sv8qt", "Level 5", 5),
    ("bingo_showdown", "event_callback_14h0b2", "14h0b2", "Level 10", 10),
    ("bingo_showdown", "event_callback_livykp", "livykp", "Level 15", 15),
    ("bingo_showdown", "event_callback_95ye13", "95ye13", "Level 20", 20),
    ("bingo_showdown", "event_callback_fjp3vm", "fjp3vm", "Level 25", 25),
    ("bingo_showdown", "event_callback_upmo7s", "upmo7s", "Level 50", 50),
    ("bingo_showdown", "event_callback_jkpze3", "jkpze3", "First Purchase", 0),

    # Blast Friends
    ("blast_friends", "event_callback_v5zsay", "v5zsay", "Reach Level 20", 20),
    ("blast_friends", "event_callback_qco1yc", "qco1yc", "Level 50", 50),
    ("blast_friends", "event_callback_nmbpbj", "nmbpbj", "Level 100", 100),
    ("blast_friends", "event_callback_7tcb9y", "7tcb9y", "Level 250", 250),
    ("blast_friends", "event_callback_a0tksk", "a0tksk", "Level 500", 500),
    ("blast_friends", "event_callback_r9ojpu", "r9ojpu", "Level 1000", 1000),
    ("blast_friends", "event_callback_8q1rrv", "8q1rrv", "Level 2000", 2000),

    # Block Blitz
    ("block_blitz", "event_callback_z9gmw7", "z9gmw7", "Win Journey Level 5", 5),
    ("block_blitz", "event_callback_erj7x3", "erj7x3", "Level 10", 10),
    ("block_blitz", "event_callback_1v5jpk", "1v5jpk", "Level 20", 20),
    ("block_blitz", "event_callback_1puzhk", "1puzhk", "Level 30", 30),
    ("block_blitz", "event_callback_fxhwo0", "fxhwo0", "Level 40", 40),
    ("block_blitz", "event_callback_bqkl2c", "bqkl2c", "Level 50", 50),
    ("block_blitz", "event_callback_tum80y", "tum80y", "Level 70", 70),
    ("block_blitz", "event_callback_nm5hzf", "nm5hzf", "Level 100", 100),
    ("block_blitz", "event_callback_ulzxtz", "ulzxtz", "Level 150", 150),
    ("block_blitz", "event_callback_q7kns1", "q7kns1", "Level 300", 300),
    ("block_blitz", "event_callback_uf24fv", "uf24fv", "Level 500", 500),
    ("block_blitz", "event_callback_vjp76b", "vjp76b", "Level 700", 700),
    ("block_blitz", "event_callback_nxjpvy", "nxjpvy", "Level 1000", 1000),
    ("block_blitz", "event_callback_1020304", "1020304", "First Time Purchase", 0),

    # Block Joy
    ("block_joy", "event_callback_dvo8mu", "dvo8mu", "Level 5", 5),
    ("block_joy", "event_callback_r45ld3", "r45ld3", "Level 10", 10),
    ("block_joy", "event_callback_61mki6", "61mki6", "Level 20", 20),
    ("block_joy", "event_callback_15q1fg", "15q1fg", "Level 30", 30),
    ("block_joy", "event_callback_1ziiag", "1ziiag", "Level 50", 50),
    ("block_joy", "event_callback_yh508k", "yh508k", "Level 70", 70),
    ("block_joy", "event_callback_3gxgyp", "3gxgyp", "Level 100", 100),
    ("block_joy", "event_callback_vev8ur", "vev8ur", "Level 150", 150),
    ("block_joy", "event_callback_nazx5v", "nazx5v", "Level 300", 300),
    ("block_joy", "event_callback_q98rl6", "q98rl6", "Level 500", 500),
    ("block_joy", "event_callback_v1htdn", "v1htdn", "Level 700", 700),
    ("block_joy", "event_callback_soa9vy", "soa9vy", "Level 1000", 1000),
    ("block_joy", "event_callback_c8ck9d", "c8ck9d", "First Purchase", 0),

    # Gems Adventure
    ("gems_adventure", "event_callback_dwowyx", "dwowyx", "Score 3K", 3000),
    ("gems_adventure", "event_callback_h2e11l", "h2e11l", "Score 5K", 5000),
    ("gems_adventure", "event_callback_25ud1c", "25ud1c", "Score 10K", 10000),
    ("gems_adventure", "event_callback_3vdhft", "3vdhft", "Score 25K", 25000),
    ("gems_adventure", "event_callback_amhlay", "amhlay", "Score 50K", 50000),
    ("gems_adventure", "event_callback_mkuzzm", "mkuzzm", "Score 100K", 100000),
    ("gems_adventure", "event_callback_nyi04s", "nyi04s", "Score 250K", 250000),
    ("gems_adventure", "event_callback_1v45em", "1v45em", "Score 500K", 500000),
    ("gems_adventure", "event_callback_q3tfto", "q3tfto", "Score 750K", 750000),
    ("gems_adventure", "event_callback_o9d9hb", "o9d9hb", "Score 1M", 1000000),

    # Bravo Slots
    ("bravo_slots", "event_callback_pxnk4e", "pxnk4e", "Reach Level 40", 40),
    ("bravo_slots", "event_callback_k6p17i", "k6p17i", "Reach Level 100", 100),
    ("bravo_slots", "event_callback_fw0837", "fw0837", "Purchase Mission Pass", 0),
    ("bravo_slots", "event_callback_i1l8xp", "i1l8xp", "Reach Level 200", 200),
    ("bravo_slots", "event_callback_nlql3m", "nlql3m", "Reach Level 400", 400),
    ("bravo_slots", "event_callback_1pvoa2", "1pvoa2", "Accum Purchase $9.99", 0),
    ("bravo_slots", "event_callback_96j1vw", "96j1vw", "Reach Level 800", 800),
    ("bravo_slots", "event_callback_jpw7pe", "jpw7pe", "Level 2000", 2000),
    ("bravo_slots", "event_callback_y85bjt", "y85bjt", "Level 4000", 4000),

    # Cash Storm
    ("cash_storm", "event_callback_ht80ad", "ht80ad", "Complete Level 15", 15),
    ("cash_storm", "event_callback_ll59t0", "ll59t0", "Purchase any $9.99", 0),
    ("cash_storm", "event_callback_47akr5", "47akr5", "Level 30", 30),
    ("cash_storm", "event_callback_yjd7i0", "yjd7i0", "Level 40", 40),
    ("cash_storm", "event_callback_fmwgmq", "fmwgmq", "Level 60", 60),
    ("cash_storm", "event_callback_6nulf0", "6nulf0", "Purchase any $19.9", 0),
    ("cash_storm", "event_callback_6ppgib", "6ppgib", "Level 80", 80),
    ("cash_storm", "event_callback_qyasgc", "qyasgc", "Level 100", 100),

    # Climb Mountain
    ("climb_mountain", "event_callback_xt4epl", "xt4epl", "Complete Level 25", 25),
    ("climb_mountain", "event_callback_n2qh1u", "n2qh1u", "Level 100", 100),
    ("climb_mountain", "event_callback_bssey9", "bssey9", "Level 300", 300),

    # Clock Maker
    ("clock_maker", "event_callback_uu8lcy", "uu8lcy", "Unlock Stables", 1),
    ("clock_maker", "event_callback_64yi1x", "64yi1x", "Unlock the Mill", 2),
    ("clock_maker", "event_callback_gwqs4i", "gwqs4i", "Unlock Old Sam's House", 3),
    ("clock_maker", "event_callback_uqry54", "uqry54", "Unlock Harrison's Mansion", 4),
    ("clock_maker", "event_callback_1nwuqr", "1nwuqr", "Unlock Fire Station", 5),
    ("clock_maker", "event_callback_as93wo", "as93wo", "Unlock Antique Shop", 6),
    ("clock_maker", "event_callback_86t122", "86t122", "Unlock Theatre", 7),
    ("clock_maker", "event_callback_t912za", "t912za", "Unlock School", 8),
    ("clock_maker", "event_callback_senibm", "senibm", "Unlock Fountain", 9),
    ("clock_maker", "event_callback_g8g4p2", "g8g4p2", "Unlock the Clock Tower", 10),
    ("clock_maker", "event_callback_bev80p", "bev80p", "Purchase", 0),

    # Hot Rolls Dice
    ("hot_rolls_dice", "event_callback_66d4hu", "66d4hu", "Watch Ad", 0),
]


def _build_index():
    """يبني فهارس ثابتة للألعاب والأحداث لتسريع الاستعلام."""
    games = []
    events_by_game = {}
    for i, (name, display_name, app_token, emoji) in enumerate(ADJ_GAMES, start=1):
        game = {
            "id": i,
            "name": name,
            "display_name": display_name,
            "app_token": app_token,
            "emoji": emoji,
        }
        games.append(game)
        events_by_game[name] = []

    event_id = 1
    for (game_name, event_name, event_token, display_name, level_value) in ADJ_EVENTS:
        ev = {
            "id": event_id,
            "game_id": None,
            "game_name": game_name,
            "event_name": event_name,
            "event_token": event_token,
            "display_name": display_name,
            "level_value": level_value if level_value is not None else 0,
        }
        events_by_game.setdefault(game_name, []).append(ev)
        event_id += 1

    for game in games:
        for ev in events_by_game.get(game["name"], []):
            ev["game_id"] = game["id"]

    return games, events_by_game


_GAMES, _EVENTS_BY_GAME = _build_index()
_EVENTS_INDEX = {}
for _evs in _EVENTS_BY_GAME.values():
    for _e in _evs:
        _EVENTS_INDEX[_e["id"]] = _e


def get_all_games_adj() -> list:
    """قائمة كل ألعاب Adjust مرتبة حسب الاسم المعروض."""
    return sorted(_GAMES, key=lambda g: g["display_name"])


def get_game_adj_by_id(game_id: int):
    """يرجع لعبة Adjust بمعرفها أو None."""
    for g in _GAMES:
        if g["id"] == game_id:
            return g
    return None


def get_adj_events(game_id: int) -> list:
    """قائمة أحداث لعبة Adjust مرتبة حسب level_value (مطابق للبوت المرجعي)."""
    return sorted(
        _EVENTS_BY_GAME.get(get_game_adj_by_id(game_id)["name"], []),
        key=lambda e: e["level_value"],
    ) if get_game_adj_by_id(game_id) else []


def get_adj_event_by_id(event_id: int):
    """يرجع حدث Adjust بمعرفه أو None."""
    return _EVENTS_INDEX.get(event_id)


def search_adj_games(text: str) -> list:
    """بحث في ألعاب Adjust حسب الاسم المعروض."""
    text = text.strip().lower()
    if not text:
        return []
    return [g for g in _GAMES if text in g["display_name"].lower()]
