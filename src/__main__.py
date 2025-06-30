"""Entry point for running the src package as a module."""

if __name__ == "__main__":
    from .app import main
    import os
    
    rtsp_url = os.getenv("RTSP_URL")
    if rtsp_url:
        main(rtsp_url)
    else:
        print("RTSP_URL environment variable not set")
