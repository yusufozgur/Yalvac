""" Manage sessions logic here"""
from datetime import datetime

def add_session_availability_request(chat_id,
                                     sessions_requests_data,
                                     selected_datetime):
    #add datetime as key if not already in the sessions_requests_data
    if selected_datetime not in sessions_requests_data.keys():
        sessions_requests_data[selected_datetime] = []
    
    #chatid to the datetime
    sessions_requests_data[selected_datetime].append(chat_id)
    pass


def remove_session_availability_request(chat_id,
                                     sessions_requests_data,
                                     selected_datetime):
    sessions_requests_data[selected_datetime].remove(chat_id)
    pass

def get_following_sessions_for_chatid(chat_id,
                                     sessions_requests_data) -> list[datetime]:
    """return sessions followed by chatid in a formatted string list"""
    following_sessions=[]
    for session, chatids in sessions_requests_data.items():
        if chat_id in chatids:
            following_sessions.append(session)
    return(following_sessions)