

users = {
    "user1": "password1",
    "user2": "password2",
    # Add more users as needed
}

def check_credentials(username, password):
    return users.get(username) == password
