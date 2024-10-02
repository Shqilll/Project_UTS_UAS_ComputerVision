import cv2
import numpy as np
from skimage import exposure
import os

def read_video(filepath):
    cap = cv2.VideoCapture(filepath)
    frames = []
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        frames.append(frame)
    cap.release()
    return frames

def convert_to_grayscale(frames):
    return [cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) for frame in frames]

def histogram_equalization(frames):
    return [cv2.equalizeHist(frame) for frame in frames]

def contrast_stretching(frames):
    stretched_frames = []
    for frame in frames:
        p2, p98 = np.percentile(frame, (2, 98))
        stretched = exposure.rescale_intensity(frame, in_range=(p2, p98))
        stretched_frames.append(stretched)
    return stretched_frames

def clahe(frames):
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    return [clahe.apply(frame) for frame in frames]

def median_filter(frames):
    return [cv2.medianBlur(frame, 5) for frame in frames]

def calculate_mse(original, processed):
    return np.mean((original - processed) ** 2)

def calculate_psnr(original, processed):
    mse = calculate_mse(original, processed)
    if mse == 0:
        return float('inf')
    max_pixel = 255.0
    return 20 * np.log10(max_pixel / np.sqrt(mse))

def evaluate(frames, processed_frames):
    mse_values = [calculate_mse(orig, proc) for orig, proc in zip(frames, processed_frames)]
    psnr_values = [calculate_psnr(orig, proc) for orig, proc in zip(frames, processed_frames)]
    avg_mse = np.mean(mse_values)
    avg_psnr = np.mean(psnr_values)
    return avg_mse, avg_psnr

def save_frames(frames, folder, prefix):
    if not os.path.exists(folder):
        os.makedirs(folder)
    for i, frame in enumerate(frames):
        filename = os.path.join(folder, f"{prefix}_frame_{i}.png")
        cv2.imwrite(filename, frame)

def process_video(video_path):
    frames = read_video(video_path)
    gray_frames = convert_to_grayscale(frames)

    he_frames = histogram_equalization(gray_frames)
    cs_frames = contrast_stretching(gray_frames)
    clahe_frames = clahe(gray_frames)

    he_filtered = median_filter(he_frames)
    cs_filtered = median_filter(cs_frames)
    clahe_filtered = median_filter(clahe_frames)

    he_mse, he_psnr = evaluate(gray_frames, he_filtered)
    cs_mse, cs_psnr = evaluate(gray_frames, cs_filtered)
    clahe_mse, clahe_psnr = evaluate(gray_frames, clahe_filtered)

    print(f'Video: {video_path}')
    print(f'HE - MSE: {he_mse}, PSNR: {he_psnr}')
    print(f'CS - MSE: {cs_mse}, PSNR: {cs_psnr}')
    print(f'CLAHE - MSE: {clahe_mse}, PSNR: {clahe_psnr}')
    print('')

    base_folder = os.path.splitext(video_path)[0]
    save_frames(frames, base_folder, "normal")
    save_frames(gray_frames, base_folder, "grayscale")
    save_frames(he_frames, base_folder, "he")
    save_frames(cs_frames, base_folder, "cs")
    save_frames(clahe_frames, base_folder, "clahe")

def process_folder(folder_path):
    for filename in os.listdir(folder_path):
        if filename.endswith('.avi'):
            video_path = os.path.join(folder_path, filename)
            process_video(video_path)

# Define the paths to the two folders
folder_path1 = 'D:\\Kuliah\\Semester 7\\Computer Vision\\UTS_COMVIS\\Video_UTS\\UCF50\\PlayingViolin'
folder_path2 = 'D:\\Kuliah\\Semester 7\\Computer Vision\\UTS_COMVIS\\Video_UTS\\UCF50\\HorseRace'

# Process each folder
process_folder(folder_path1)
process_folder(folder_path2)