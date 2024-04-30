from flask import Flask, render_template, request, jsonify
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import io
import base64

app = Flask(_name_)

def plot_recommendation(data):
    # Determine the data types present in the dataset
    data_types = data.dtypes

    # Categorize columns based on data types
    numerical_cols = data_types[data_types != 'object'].index.tolist()
    categorical_cols = data_types[data_types == 'object'].index.tolist()

    # Plot recommendation based on the type of data
    plots = []

    if len(numerical_cols) > 0:
        # If numerical data present, recommend plots for numerical data
        for col in numerical_cols:
            # Create a figure and axis for each plot
            fig, ax = plt.subplots(figsize=(8, 6))

            if len(data[col].unique()) > 10:
                # For continuous numerical data, recommend histogram
                sns.histplot(data[col], kde=True, ax=ax)
                ax.set_title(f'Histogram of {col}')
            else:
                # For discrete numerical data, recommend count plot
                sns.countplot(data=data, x=col, ax=ax)
                ax.set_title(f'Count Plot of {col}')
                ax.set_ylabel('Count')

            # Save the plot as an image and encode it as base64
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png')
            plt.close(fig)
            buffer.seek(0)
            plot_data = base64.b64encode(buffer.read()).decode('utf-8')
            plots.append({'name': col, 'type': 'image/png', 'data': plot_data})

    if len(categorical_cols) > 0:
        # If categorical data present, recommend plots for categorical data
        for col in categorical_cols:
            # Create a figure and axis for each plot
            fig, ax = plt.subplots(figsize=(8, 6))

            # Count plot for categorical data
            sns.countplot(data=data, x=col, ax=ax)
            ax.set_title(f'Count Plot of {col}')
            ax.set_xlabel(col)
            ax.set_ylabel('Count')
            ax.tick_params(axis='x', rotation=45)

            # Save the plot as an image and encode it as base64
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png')
            plt.close(fig)
            buffer.seek(0)
            plot_data = base64.b64encode(buffer.read()).decode('utf-8')
            plots.append({'name': col, 'type': 'image/png', 'data': plot_data})

    return plots

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    # Check if a file was uploaded
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'})

    file = request.files['file']

    # Check if the file has a valid extension
    if file.filename == '':
        return jsonify({'error': 'No file selected'})

    if file and file.filename.endswith('.csv'):
        # Read the CSV file into a DataFrame
        df = pd.read_csv(file)

        # Call the plot_recommendation function with the DataFrame
        plots = plot_recommendation(df)

        return jsonify({'plots': plots})

    return jsonify({'error': 'Invalid file format'})

if _name_ == '_main_':
    app.run(debug=True)