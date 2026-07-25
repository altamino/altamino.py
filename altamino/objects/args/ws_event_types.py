class wsEvent:
    """
    types of socket events in altamino

    attributes:
    - __slots__ (list of all attributes)
    """
    __slots__ = (
        "chat_action_start", "chat_action_end", "chat_message", "notification",
        "socket_error_message", "socket_exception_message", "typing_start", "recording_start",
        "typing_end", "recording_end",

        "on_text_message", "on_image_message", "on_youtube_message", "on_strike_message",
        "on_voice_message", "on_sticker_message", "on_voice_chat_not_answered",
        "on_voice_chat_not_cancelled", "on_voice_chat_not_declined", "on_video_chat_not_answered",
        "on_video_chat_not_cancelled", "on_video_chat_not_declined", "on_avatar_chat_not_answered",
        "on_avatar_chat_not_cancelled", "on_avatar_chat_not_declined", "on_delete_message",
        "on_group_member_join", "on_group_member_leave", "on_session_init",
        "on_chat_background_changed", "on_chat_title_changed", "on_chat_icon_changed",
        "on_voice_chat_start", "on_video_chat_start", "on_avatar_chat_start", "on_voice_chat_end",
        "on_video_chat_end", "on_avatar_chat_end", "on_chat_content_changed", "on_screen_room_start",
        "on_screen_room_end", "on_chat_host_transfered", "on_text_message_force_removed",
        "on_chat_removed_message", "on_text_message_removed_by_admin", "on_chat_tip",
        "on_chat_pin_announcement", "on_voice_chat_permission_open_to_everyone",
        "on_voice_chat_permission_invited_and_requested", "on_voice_chat_permission_invite_only",
        "on_chat_view_only_enabled", "on_chat_view_only_disabled", "on_chat_unpin_announcement",
        "on_chat_tipping_enabled", "on_chat_tipping_disabled", "on_timestamp_message",
        "on_welcome_message", "on_invite_message",

        "on_user_membership", "on_user_membership_invitation", "on_comment", "on_reply",
        "on_vote_up", "on_repost", "on_message_notification", "on_chat_typing",
        "on_thread_user_observing", "on_chat_thread_invite", "on_join_request_received",
        "on_join_request_approved", "on_invite_to_voice_chat_notification",
        "on_invite_to_video_chat_notification", "on_invite_to_screening_room",
        "on_vv_chat_presenter_invite", "on_chat_add_cohost", "on_chat_remove_cohost",

        "ANY",
    )


for obj in wsEvent.__slots__:
    setattr(wsEvent, obj, obj)


ws_message_methods = {
    304: "chat_action_start",
    306: "chat_action_end",
    1000: "chat_message",
    10: "notification",
    1: "socket_error_message",
    305: "socket_exception_message",
}

ws_chat_action_start = {
    "Typing": "typing_start",
    "Recording": "recording_start",
}

ws_chat_action_end = {
    "Typing": "typing_end",
    "Recording": "recording_end",
}


notification_types = {
    1: "on_user_membership",
    2: "on_user_membership_invitation",
    3: "on_comment",
    7: "on_reply",
    9: "on_vote_up",
    11: "on_repost",
    18: "on_message_notification",
    19: "on_chat_typing",
    20: "on_thread_user_observing",
    21: "on_chat_invite",          # реальный инвайт в чат
    22: "on_join_request_received",
    23: "on_join_request_approved",
    29: "on_invite_to_voice_chat_notification",
    30: "on_invite_to_video_chat_notification",
    37: "on_invite_to_screening_room",
    66: "on_vv_chat_presenter_invite",
    67: "on_chat_add_cohost",
    68: "on_chat_remove_cohost",
}

ws_message_types = {
    "ANY": "ANY",
    "0:0": "on_text_message",
    "0:100": "on_image_message",
    "0:103": "on_youtube_message",
    "1:0": "on_strike_message",
    "2:110": "on_voice_message",
    "3:113": "on_sticker_message",
    "52:0": "on_voice_chat_not_answered",
    "53:0": "on_voice_chat_not_cancelled",
    "54:0": "on_voice_chat_not_declined",
    "55:0": "on_video_chat_not_answered",
    "56:0": "on_video_chat_not_cancelled",
    "57:0": "on_video_chat_not_declined",
    "58:0": "on_avatar_chat_not_answered",
    "59:0": "on_avatar_chat_not_cancelled",
    "60:0": "on_avatar_chat_not_declined",
    "100:0": "on_delete_message",
    "101:0": "on_group_member_join",
    "102:0": "on_group_member_leave",
    "103:0": "on_session_init",
    "104:0": "on_chat_background_changed",
    "105:0": "on_chat_title_changed",
    "106:0": "on_chat_icon_changed",
    "107:0": "on_voice_chat_start",
    "108:0": "on_video_chat_start",
    "109:0": "on_avatar_chat_start",
    "110:0": "on_voice_chat_end",
    "111:0": "on_video_chat_end",
    "112:0": "on_avatar_chat_end",
    "113:0": "on_chat_content_changed",
    "114:0": "on_screen_room_start",
    "115:0": "on_screen_room_end",
    "116:0": "on_chat_host_transfered",
    "117:0": "on_text_message_force_removed",
    "118:0": "on_chat_removed_message",
    "119:0": "on_text_message_removed_by_admin",
    "120:0": "on_chat_tip",
    "121:0": "on_chat_pin_announcement",
    "122:0": "on_voice_chat_permission_open_to_everyone",
    "123:0": "on_voice_chat_permission_invited_and_requested",
    "124:0": "on_voice_chat_permission_invite_only",
    "125:0": "on_chat_view_only_enabled",
    "126:0": "on_chat_view_only_disabled",
    "127:0": "on_chat_unpin_announcement",
    "128:0": "on_chat_tipping_enabled",
    "129:0": "on_chat_tipping_disabled",
    "65281:0": "on_timestamp_message",
    "65282:0": "on_welcome_message",
    "65283:0": "on_invite_message",
}