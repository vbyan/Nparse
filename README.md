<br>
<img src="https://raw.githubusercontent.com/vbyan/Nparse/main/astronaut.png" style="width:80px; height:100px; margin-top:50px;">

# Welcome to Deeva 👋

**Analytics toolkit designed for rapid insights into Object Detection datasets.**

## What is Deeva?

Deeva provides a flexible, interactive environment for exploring and analyzing **Object Detection** data, suitable for both quick exploratory analysis and production-grade reporting. Built with **Streamlit** and designed with user-friendliness in mind, Deeva is both accessible to newcomers and powerful for experienced users.
### Features

- **Interactive Dashboards**: Effortlessly create interactive dashboards for immediate, in-depth data exploration.
- **Instant Access**: Start visualizing data instantly by launching with a specified folder path.
- **Flexible Command-Line Interface**: Launch Deeva with ease using custom paths and configurations directly from the command line.
- **Built-in Toy Datasets**: Experiment and get started quickly with the pre-installed `coco128` dataset.

## Installation

Open a terminal and run:

```bash
$ pip install deeva
```

To run it separately in a *virtual environment:*

```bash
$ python3 -m venv myenv
$ source myenv/bin/activate

$ pip install deeva
```

## Quickstart
When **Deeva** is installed just run:
```bash
$ deeva start
```

This opens the app's **input page**, where you need to specify the **data path**.

<img src="https://raw.githubusercontent.com/vbyan/Nparse/main/input_page.gif" width=400></img>

### Data structure

Provided **directory** should be organized as follows:

```plaintext
data-path/
├── images/        # Folder containing image files (e.g., .jpg, .png)
├── labels/        # Folder containing label files (e.g., .txt, .json)
└── labelmap.txt   # A file mapping class IDs to class labels (optional)
```

## Insights

Deeva offers a comprehensive suite of **statistical insights** to help you understand your dataset at a granular level. The main statistics available in the app include:

### 1. **File Matching and Integrity**

- **Image-Label Matching**: Derives statistics on how many **images** have **corresponding labels** and vice versa
- **Filename Consistency**: Checks for **corrupted** or **misaligned** files in images and labels

<br>
<img src="https://raw.githubusercontent.com/vbyan/Nparse/main/data_match.gif" width=400>

### 2. **Dataset Overview**

- **Formats and Backgrounds**: `yolo` **vs** `voc`, Images **vs** Backgrounds, `jpeg` **vs** `jpg` **vs** `png`.
- **Class distribution**: Provides a **count of instances and images** per class, giving a quick view of class  **imbalance**.
- **Class Co-occurrence**: Analyzes how often different classes **appear together**.

<br>
<img src="https://raw.githubusercontent.com/vbyan/Nparse/main/overall.gif" width=400>


### 3. **Annotation Statistics**

- **Annotation Counts**: Displays the total number of annotations, broken down by class.
- **Bounding Box Analysis**: Summarizes the sizes, shapes, and aspect ratios of bounding boxes across classes, which can be useful for model tuning.
- **Density Distribution**: Maps annotation density to show where the most annotated regions of images are located.

### 4. **Image Statistics**

- **Image Count & Resolutions**: Provides the total image count and common resolutions, allowing you to standardize or adjust image preprocessing steps.
- **Image Dimensions**: Analyzes the height, width, and aspect ratios of images across the dataset.
- **Format Frequencies**: Lists the distribution of file formats (e.g., `.jpg`, `.png`) to support format standardization.

### 5. **Annotation Overlaps**

- **Bounding Box Overlap**: Measures overlap between bounding boxes to detect potential issues in annotation quality.
- **Intersection Over Union (IoU)**: Calculates IoU for overlapping annotations to help detect annotation inconsistencies.
- **Class Overlap Patterns**: Shows common patterns of class overlap to better understand spatial relationships within images.

Each of these insights helps to validate and prepare your dataset for analysis or model training, ensuring data quality and enabling informed decision-making during preprocessing and model development.




## License

Deeva is completely free and open-source and licensed under the [Apache 2.0](https://www.apache.org/licenses/LICENSE-2.0) license.
