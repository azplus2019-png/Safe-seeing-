import os
import sys
import time

def create_test_video(path):
    print(f"Creating test video at {path}...")
    # Create a 3-second black video with a beep
    # This requires ffmpeg to be installed
    os.system(f"ffmpeg -f lavfi -i color=c=black:s=640x480:d=3 -f lavfi -i 'sine=frequency=1000:duration=3' -c:v libx264 -c:a aac -pix_fmt yuv420p {path} -y")

def smoke_test(mock=False):
    input_video = "test_input.mp4"
    output_video = "test_output.mp4"
    
    if not os.path.exists(input_video):
        create_test_video(input_video)
    
    if mock:
        print("Running MOCK smoke test...")
        time.sleep(2)
        print("Mock: Initializing models...")
        time.sleep(1)
        print("Mock: Pre-scanning audio...")
        time.sleep(1)
        print("Mock: Pre-scanning visual...")
        time.sleep(2)
        print("Mock: Applying filters and rendering...")
        time.sleep(2)
        print(f"Mock Success! Safe video saved to: {output_video}")
        with open(output_video, "w") as f:
            f.write("mock video content")
        return

    from safe_seeing import SafeSeeing
    print("Running REAL smoke test...")
    try:
        # Use a higher sampling rate for a short clip
        engine = SafeSeeing(sample_fps=5.0)
        engine.run(input_video, output_video)
        print("Real smoke test PASSED!")
    except Exception as e:
        print(f"Real smoke test FAILED: {e}")
        sys.exit(1)

if __name__ == "__main__":
    is_mock = "--mock" in sys.argv
    smoke_test(mock=is_mock)
