from django.contrib.sessions.models import Session

# Retrieve all sessions from the database
def check():
    all_sessions = Session.objects.all()

    # Print information about each session
    for session in all_sessions:
        session_data = session.get_decoded()
        print(f"Session Key: {session.session_key}, Data: {session_data}")
    return session.session_key
def clear(key):
    session_key_to_clear = key

    try:
        # Retrieve the session object using the session key
        session_to_clear = Session.objects.get(session_key=session_key_to_clear)

        # Clear the session data
        session_to_clear.delete()
        print(f"Session with key '{session_key_to_clear}' has been cleared.")

    except Session.DoesNotExist:
        print(f"Session with key '{session_key_to_clear}' does not exist.")

# Call the check function

