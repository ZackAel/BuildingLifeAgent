import data_utils
from social_features import matching_algorithm, community_board, achievement_cards


def test_match_partners():
    users = {
        'alice': ['ai', 'fitness'],
        'bob': ['ai', 'cooking'],
        'carol': ['fitness', 'gym']
    }
    matches = matching_algorithm.match_partners(users)
    assert matches['alice'] in {'bob', 'carol'}
    assert matches['bob'] == 'alice'


def test_community_board(tmp_path, monkeypatch):
    monkeypatch.setattr(data_utils, 'DATA_DIR', tmp_path)
    community_board.post_commitment('alice', 'Finish project')
    community_board.post_commitment('bob', 'Run marathon')
    items = community_board.get_commitments()
    assert ('alice', 'Finish project') in items
    assert ('bob', 'Run marathon') in items


def test_achievement_card():
    card = achievement_cards.create_card('Wins', ['Task1', 'Task2'])
    assert 'Wins' in card
    assert 'Task1' in card
    assert card.startswith('+') and card.endswith('+')
