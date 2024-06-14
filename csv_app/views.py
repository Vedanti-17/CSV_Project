from django.shortcuts import render
from django.http import HttpResponseRedirect
from .forms import UploadCSVForm
import pandas as pd
import matplotlib.pyplot as plt
import os

def handle_uploaded_file(f):
    file_path = f'media/{f.name}'
    with open(file_path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    return file_path

def read_uploaded_csv(file_path):
    df = pd.read_csv(file_path)
    return df

def upload_file(request):
    if request.method == 'POST':
        form = UploadCSVForm(request.POST, request.FILES)
        if form.is_valid():
            file_path = handle_uploaded_file(request.FILES['csv_file'])
            return HttpResponseRedirect('/analyze/' + os.path.basename(file_path))
    else:
        form = UploadCSVForm()
    return render(request, 'upload.html', {'form': form})

from django.shortcuts import render
from django.http import HttpResponse
from .forms import UploadCSVForm
import csv
import os
from django.conf import settings

def upload_csv(request):
    if request.method == 'POST':
        form = UploadCSVForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['csv_file']
            # Save the file to the media directory
            file_path = os.path.join(settings.MEDIA_ROOT, csv_file.name)
            with open(file_path, 'wb+') as destination:
                for chunk in csv_file.chunks():
                    destination.write(chunk)
            # Process the uploaded CSV file
            with open(file_path, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                # Skip header
                next(reader)
                for row in reader:
                    print(row)
            return HttpResponse('File uploaded and processed successfully')
    else:
        form = UploadCSVForm()
    return render(request, 'upload.html', {'form': form})

# views.py

from django.shortcuts import render, redirect
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64

def upload_file(request):
    if request.method == 'POST' and request.FILES['csv_file']:
        csv_file = request.FILES['csv_file']
        df = pd.read_csv(csv_file)
        # Process df as needed
        request.session['df'] = df.to_html()
        return redirect('data_analysis_results')
    return render(request, 'upload_file.html')

def data_analysis_results(request):
    df = pd.read_html(request.session['df'])[0]
    summary_stats = df.describe()
    missing_values = df.isnull().sum()
    # Generate histograms
    plt.hist(df['numerical_column'])
    plt.xlabel('Values')
    plt.ylabel('Frequency')
    plt.title('Histogram')
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img_url = base64.b64encode(img.getvalue()).decode()
    plt.close()
    return render(request, 'data_analysis_results.html', {'df': df.to_html(), 'summary_stats': summary_stats.to_html(), 'missing_values': missing_values.to_html(), 'img_url': img_url})

def data_analysis_results(request):
    # Your data processing code here
    return render(request, 'data_analysis_results.html', {'img_url': img_url})

def analyze_file(request, filename):
    file_path = f'media/{filename}'
    df = read_uploaded_csv(file_path)

    # Displaying first few rows of the data
    first_few_rows = df.head().to_html()

    # Calculating summary statistics
    summary_stats = df.describe().to_html()

    # Identifying and handling missing values
    missing_values = df.isnull().sum().to_html()

    # Generating histograms
    plt.figure(figsize=(10, 6))
    df.hist()
    plt.tight_layout()
    hist_path = f'media/{filename}_hist.png'
    plt.savefig(hist_path)
    plt.close()

    context = {
        'filename': filename,
        'first_few_rows': first_few_rows,
        'summary_stats': summary_stats,
        'missing_values': missing_values,
        'histogram': hist_path
    }
    return render(request, 'analyze.html', context)
