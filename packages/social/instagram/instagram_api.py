# Import the 'requests' library, which is used for making HTTP requests
import requests
from dotenv import find_dotenv, load_dotenv
import os

# Define a class named 'InstagramAPI'
class InstagramAPI:
    # Constructor method (__init__) with 'access_token' as a parameter
    def __init__(self, access_token):
        # Initialize an instance variable 'access_token' with the provided value
        self.access_token = access_token
        # Initialize an instance variable 'api_url' with the Instagram Graph API base URL
        self.api_url = "https://graph.instagram.com/v12.0"

    # Define a method 'make_request' for making HTTP requests to the Instagram Graph API
    def make_request(self, endpoint, params=None, method="GET", files=None):
        # Construct the complete URL for the API endpoint
        url = f"{self.api_url}/{endpoint}"
        # Set the headers for the request, including the authorization token
        headers = {"Authorization": f"Bearer {self.access_token}"}
        
        # Check the HTTP method and make the corresponding request
        if method == "GET":
            response = requests.get(url, headers=headers, params=params)
        elif method == "POST":
            response = requests.post(url, headers=headers, params=params, files=files)
        else:
            # Raise an exception for unsupported HTTP methods
            raise ValueError("Unsupported HTTP Method")
        
        # Check for HTTP errors and raise an exception if necessary
        response.raise_for_status()
        # Parse the response as JSON and return the result
        return response.json()
    

    # Define a method 'publish_photo' to upload and publish a photo to Instagram
    def publish_photo(self, caption, image_path):
        # Define parameters for uploading a photo
        upload_params = {
            "caption": caption,
            "access_token": self.access_token,
        }
        
        # Construct the URL for uploading a photo to the user's account
        upload_url = f"{self.api_url}/me/photos"
        # Prepare the photo file for upload
        files = {"file": open(image_path, "rb")}
        # Make a request to upload the photo and get the response
        upload_response = self.make_request(upload_url, params=upload_params, method="POST", files=files)

        # Get the media ID from the upload response
        media_id = upload_response.get("id")

        # Define parameters for publishing the post
        publish_params = {
            "caption": caption,
            "access_token": self.access_token,
            "attached_media": f'{{"media_id":"{media_id}"}}',
        }

        # Construct the URL for publishing the post
        publish_url = f"{self.api_url}/me/media_publish"
        # Make a request to publish the post
        self.make_request(publish_url, params=publish_params, method="POST")

        # Print a success message
        print("Post published successfully!")

# Example usage:
if __name__ == "__main__":
    # Load env file
    load_dotenv(find_dotenv())

    try:
        access_token = os.environ["INSTAGRAM_ACCESS_TOKEN"]
    except KeyError:
        access_token = os.environ.get("INSTAGRAM_ACCESS_TOKEN")
    
    # Create an instance of the InstagramAPI class with the access token
    instagram_api = InstagramAPI(access_token)

    # Define a caption and the file path to the photo to be uploaded
    caption = "Hello, Instagram! 🌟"
    image_path = "path/to/your/photo.jpg"

    # Call the 'publish_photo' method to upload and publish the photo
    instagram_api.publish_photo(caption, image_path)
