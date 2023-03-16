import os


def main():
    folder = 'BackgroundVideos'

    for count, filename in enumerate(os.listdir(folder)):

        if '.mp4' not in filename:
            continue 

        name = f'Rename_{str(count)}.mp4'
        src = f'{folder}/{filename}'
        rename = f'{folder}/{name}'


        os.rename(src, rename)

    for count, filename in enumerate(os.listdir(folder)):

        if '.mp4' not in filename:
            continue 

        if 'Rename' not in filename:
            continue

        name = f'ShortTemplate_{str(count)}.mp4'
        src = f'{folder}/{filename}'
        rename = f'{folder}/{name}'


        os.rename(src, rename)

if __name__ == '__main__':
    main()