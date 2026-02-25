from controller.main_controller import run_app
from model import datasets as ds

def main():
    file_name = r"C:\Users\Study\PycharmProjects\CS490R\treemap-heatmap-research\model\songs_normalize.csv"

    df = ds.load_dataset(file_name)

    genre_list = ds.load_genre_list(df)

    run_app(df, genre_list)

if __name__ == "__main__":
    main()