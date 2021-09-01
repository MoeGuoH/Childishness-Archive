from PIL import Image, ImageDraw, ImageFilter
import sys
from pyocr import pyocr
import io
import copy
import math



def RGB2HSB(rgb):
    rgb = rgb[0:3]
    hsbB = max(rgb)/255
    hsbS = 0 if max(rgb)==0 else (max(rgb)-min(rgb))/max(rgb)
    hsbH = 0
    try:
        if max(rgb)==rgb[0] and rgb[1] >= rgb[2]:
            hsbH = (rgb[1]-rgb[2]) * 60 /(max(rgb)-min(rgb))+0
        elif max(rgb)==rgb[0] and rgb[1] < rgb[2]:
            hsbH = (rgb[1]-rgb[2]) * 60 /(max(rgb)-min(rgb))+360
        elif max(rgb)==rgb[1]:
            hsbH = (rgb[2]-rgb[0]) * 60 /(max(rgb)-min(rgb))+120
        elif max(rgb)==rgb[2]:
            hsbH = (rgb[0]-rgb[1]) * 60 /(max(rgb)-min(rgb))+240
    except:
        pass
    finally:
        pass
    return (hsbH,hsbS,hsbB)

def RemoveHotPixelByColorPercentage(codeIMG, percentage_max=1, percentage_min=0, is_raw=False, showlog=False):
    rgb_list = []
    for x in range(codeIMG.size[0]):
        for y in range(codeIMG.size[1]):
            pix = codeIMG.getpixel((x, y))
            obj_rgb = list(
                filter(lambda _obj_rgb: _obj_rgb["rgb"] == pix, rgb_list))
            if len(obj_rgb) == 1:
                obj_rgb = obj_rgb[0]
                obj_rgb["count"] = obj_rgb["count"]+1
                obj_rgb["pixs"].append((x, y))
                obj_rgb["percentage"] = obj_rgb["count"] / \
                    (codeIMG.size[0]*codeIMG.size[1])
            else:
                rgb_list.append({"rgb": pix, "count": 1, "pixs": [
                                (x, y)], "percentage": 1/(codeIMG.size[0]*codeIMG.size[1])})
    result_raw = list(filter(lambda _obj_rgb: _obj_rgb["percentage"] <=
                             percentage_max and _obj_rgb["percentage"] >= percentage_min, rgb_list))
    if showlog:
        rgb_list.sort(key=lambda _obj_rgb: _obj_rgb["percentage"])
        for x in rgb_list:
            print("%s len %s %s %s" %
                  (x["rgb"], x["count"], x["pixs"][0], x["percentage"]))
        pass
    if is_raw == False:
        result = []
        for x in result_raw:
            result.extend(x["pixs"])
        return result
    return result_raw

def FixCloseBySimilarHINHSB(pix_array,img,location_range,hdiff_range,loop=1):
    result = copy.deepcopy(pix_array)
    for l in range(loop):
        for pix in pix_array:
            pix_HSB = RGB2HSB(img.getpixel(pix))
            for tage_x in range(pix[0]-location_range,pix[0]+location_range):
                for tage_y in range(pix[1]-location_range,pix[1]+location_range):
                    tmp_HSB = RGB2HSB(img.getpixel((tage_x,tage_y)))
                    if math.fabs(pix_HSB[0]-tmp_HSB[0])<math.fabs(hdiff_range) and (tage_x,tage_y) not in result:
                        result.append((tage_x,tage_y))
        pix_array = copy.deepcopy(result)
    return result

def drawPix(pix_array, a_size):
    img = Image.new("RGB", a_size, color="#ffffff")
    draw = ImageDraw.Draw(img)
    for pix in pix_array:
        draw.point(pix, fill=(0, 0, 0))
    del draw
    return img

        
if __name__ == "__main__":
    code_img = Image.open("./raw/type1.png")
    pix_array = RemoveHotPixelByColorPercentage(code_img, percentage_max=0.03, percentage_min=0.015)
    cover_img = drawPix(pix_array, code_img.size)
    cover_img = cover_img.filter(ImageFilter.SHARPEN)
    cover_img.save("./raw/type1_convert_1.png")
    pix_array = FixCloseBySimilarHINHSB(pix_array,code_img,1,5,1)
    cover_img = drawPix(pix_array, code_img.size)
    cover_img = cover_img.filter(ImageFilter.SHARPEN)
    cover_img.save("./raw/type1_convert_2.png")
    print(pyocr.tesseract.image_to_string(cover_img))
    code_img = Image.open("./raw/type2.png")
    pix_array = RemoveHotPixelByColorPercentage(code_img, percentage_max=0.2, percentage_min=0.1)
    cover_img = drawPix(pix_array, code_img.size)
    cover_img = cover_img.filter(ImageFilter.SHARPEN)
    cover_img.save("./raw/type2_convert_1.png")
    pix_array = FixCloseBySimilarHINHSB(pix_array,code_img,1,5,1)
    cover_img = drawPix(pix_array, code_img.size)
    cover_img = cover_img.filter(ImageFilter.SHARPEN)
    cover_img.save("./raw/type2_convert_2.png")
    print(pyocr.tesseract.image_to_string(cover_img))

    pass
