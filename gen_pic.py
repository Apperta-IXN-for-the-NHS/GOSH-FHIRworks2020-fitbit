from PIL import Image, ImageDraw, ImageFont, ImageChops
import pickle
import numpy as np
from datetime import datetime, timedelta

with open("full_dict", "rb") as infile:
    all_data = pickle.load(infile)

dates_to_add = {}
# Fill missing dates:
day = datetime.strptime(min(all_data, key=lambda x: datetime.strptime(x, "%Y-%m-%d")), "%Y-%m-%d")
end_day = datetime.strptime(max(all_data, key=lambda x: datetime.strptime(x, "%Y-%m-%d")), "%Y-%m-%d")
while day <= end_day:
    if day.strftime("%Y-%m-%d") not in all_data:
        dates_to_add[day.strftime("%Y-%m-%d")] = np.full(1439, fill_value=False, dtype=bool)
    day = day + timedelta(days=1)
all_data.update(dates_to_add)

first_weekend = 0
for entry_no_first_wknd, day in enumerate(all_data):
    if datetime.strptime(day, "%Y-%m-%d").weekday() == 5:
        first_weekend = entry_no_first_wknd
        break



# data = np.array([(key, all_data[key]) for key in all_data])

data = np.array(
    [entry[1] for entry in sorted([(key, all_data[key]) for key in all_data], key=lambda x: x[0])]
)
date_and_data = sorted([(key, all_data[key]) for key in all_data], key=lambda x: x[0])

img = Image.fromarray(data, mode="L")
img = img.resize((img.width, img.height * 32))
data_from_img = np.asarray(img, dtype=np.uint8) * 2
for i in range(data.shape[0], 0, -1):
    data_from_img = np.insert(data_from_img, data_from_img.shape[0] - i * 32, 1, axis=0)
for i in range(data.shape[1], 0, -60):
    data_from_img = np.insert(data_from_img, data_from_img.shape[1] - i, 1, axis=1)
data_from_img = np.insert(data_from_img, 732, 1, axis=1)

left_pad = np.full((data_from_img.shape[0], 128), 3, dtype=np.uint8)
data_from_img = np.concatenate((left_pad, data_from_img), axis=1)
top_pad = np.full((64, data_from_img.shape[1]), 3, dtype=np.uint8)
data_from_img = np.concatenate((top_pad, data_from_img), axis=0)

img = Image.fromarray(data_from_img, mode="P")
img.putpalette([255, 230, 154,  # 0 = yellow
                150, 150, 150,  # 1 = gray
                189, 215, 238,  # 2 = blue
                255, 255, 255,  # 3 = white
                0, 0, 0])  # 4 = black

d = ImageDraw.Draw(img)
# font = ImageFont.truetype(font="times", size=24)
for i, date in enumerate(date_and_data):
    # d.text((8, i * 33 + 3 + 64), date, fill=4, font=font)
    d.text((8, i * 33 + 3 + 64), date[0], fill=4)

for i in range(24):
    # d.text((i * 61 + 128 + 16, 32), f"{i:02d}:00", fill=4, font=font)
    d.text((i * 61 + 128 + 16, 32), f"{i:02d}:00", fill=4)

# darken weekends
overlay_array = np.zeros((data_from_img.shape[0], data_from_img.shape[1], 3), dtype=np.uint8)
i = first_weekend * 33 + 64
# 31 pixel per day,
# 231 per week
# 64 pixel offset at the top
while i < data_from_img.shape[0]:
    overlay_array[i:i + 66] = [20, 20, 20]
    i += 231

img = img.convert(mode="RGB")
overlay = Image.fromarray(overlay_array, mode="RGB")

# apply weekend filter
img = ImageChops.subtract(img, overlay)

img.show()
img.save("a.png")
