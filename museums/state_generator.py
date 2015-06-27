import requests

states = ['AK', 'AL', 'AR', 'AZ', 'CA', 'CO', 'CT', 'DC', 'DE', 'FL', 'GA', 'HI', 'IA', 'ID', 'IL', 'IN', 'KS', 'KY', 'LA', 'MA', 'MD', 'ME', 'MI', 'MN', 'MO', 'MS', 'MT', 'NC', 'ND', 'NE', 'NH', 'NJ', 'NM', 'NV', 'NY', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VA', 'VT', 'WA', 'WI', 'WV', 'WY',]

for state in states:
    print state
    source = requests.get("http://127.0.0.1:8000/").text

    # Disable the CSRF protection since I couldn't get it to work    
    # Get the CSRF code needed to do a POST
    token_position = source.find("name='csrfmiddlewaretoken' value='") + 34
    token = source[token_position:token_position+32]

    data = {
        'csrfmiddlewaretoken': token,
        'location': state
    }
    requests.post("http://127.0.0.1:8000/", data=data)
