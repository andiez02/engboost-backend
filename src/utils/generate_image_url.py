def generate_image_url(public_id, transformation=""):
    """Generate a Cloudinary image URL from a public ID."""
    base_url = "https://res.cloudinary.com/dxxzqzq8y/image/upload/"
    return f"{base_url}{transformation}/{public_id}"


