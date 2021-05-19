import streamlit as st
import func_util
import time

st.set_page_config(page_title='Streamlit × Spotifyで遊ぼう') # ページ情報
user_id = '31c35rzej4m25eeqcz2u2wegqzo4' # ユーザID
fu = func_util.Func(user_id) # 別で定義した関数モジュールのインスタンス

spotify = fu.spotify_auth() # Spotify認証

st.title('Streamlit × Spotifyで遊ぼう')

# 新規プレイリスト追加
with st.beta_expander('新規プレイリスト作成'):
    new_playlist_name = st.text_input('プレイリスト名の入力', '')
    add_playlist_dict_button = st.button('プレイリストを追加')
    if add_playlist_dict_button == True:
            json_add_playlist_dict = spotify.user_playlist_create(user=user_id, name=new_playlist_name, public='false')
            with st.spinner('追加しました'):
                time.sleep(3)

# 追加していくプレイリストを選択
add_playlist_dict = fu.user_playlists()
add_playlist_dict_name = st.selectbox('プレイリスト選択', list(add_playlist_dict.keys()))
playlist_id = add_playlist_dict[add_playlist_dict_name]
st.sidebar.write(add_playlist_dict_name + "に追加されている曲")

# アーティスト検索
artist_name = st.text_input('アーティスト名検索(英語名推奨)', help='ex) 東京事変➔Tokyo Incients')
if artist_name != "":
    json_artist_search = fu.artist_search(artist_name)
    related_artist_num = json_artist_search['artists']['total']
    if str(related_artist_num) == '0':
        st.error('アーティスト名でヒットしませんでした。')
    else:
        # アーティスト検索候補
        kouho_artists_dict = {}
        for kouho in json_artist_search['artists']['items']:
            kouho_artists_dict[kouho['name']] = kouho['id']
        left_column, right_column = st.beta_columns(2)
        left_column.write('検索結果')
        radio_kouho_artists = left_column.radio('', list(kouho_artists_dict.keys()))

        # 選択したアーティストの関連アーティストの検索
        artname_related_dict = {}
        artname_related_dict[radio_kouho_artists] = kouho_artists_dict[radio_kouho_artists] # 検索したアーティストを追加
        json_artist_search_related = fu.artist_related_artists(kouho_artists_dict[radio_kouho_artists])
        for artname_related in json_artist_search_related['artists']:
            artname_related_dict[artname_related['name']] = artname_related['id']
        right_column.write('関連アーティスト')
        if artname_related_dict == {}:
            right_column.warning('見つかりませんでした')
        else:
            radio_related_artists = right_column.radio('', list(artname_related_dict.keys()))
            # 関連アーティストの楽曲名とプレビュー
            left_column2, right_column2 = st.beta_columns(2)
            related_artist_top_tracks = fu.artist_top_tracks(artname_related_dict[radio_related_artists])
            left_column2.write(radio_related_artists + 'の楽曲')
            right_column2.write("楽曲プレビュー")
            check_tracks_dict = {}
            for name, uri in related_artist_top_tracks.items():
                col1, col2 = st.beta_columns(2)
                check_tracks_dict[uri['uri']] = col1.checkbox(name)
                col2.audio(uri['preview'], format='audio/wav')

            #選択した曲をプレイリストに追加
            add_track = st.button('プレイリストに曲を追加')
            if add_track == True:
                track_list = []
                for uri, check_bool in check_tracks_dict.items():
                    if check_bool == True:
                        track_list.append(uri)
                choice_add_playlist_dict = spotify.user_playlist_add_tracks(user=user_id, playlist_id=playlist_id, tracks=track_list)

# サイドバーにプレイリストの内容を表示
json_track_list = spotify.user_playlist(user=user_id, playlist_id=playlist_id, fields="tracks,next")
delete_tracks_dict = {}
for i, item in enumerate(json_track_list['tracks']['items'], start=1):
    track = item['track']
    with st.sidebar.beta_expander("   %d %32.32s %s" % (i, track['artists'][0]['name'],track['name'])):
        delete_tracks_dict[track['id']] = st.button('プレイリストから削除', key=i, help='削除しても更新がかかるまでリストに残ります')
        if delete_tracks_dict[track['id']] == True:
            track_list = []
            track_list.append(track['id'])
            spotify.user_playlist_remove_all_occurrences_of_tracks(user_id, playlist_id, track_list)
            with st.spinner('削除しました'):
                time.sleep(2)