from flask import Flask, render_template, request
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)

def generate_plot():
    optimum_tp = 160
    applied_units = int(request.form.get('units'))

    listed_shares = 29000000
    offered_shares = 4611539
    current_price = 203

    total_shares = listed_shares + offered_shares

    pre_market_cap = listed_shares * current_price

    diluted_price = round(pre_market_cap / total_shares)

    entry_arr = [100 + i for i in range(10, 50, 5)]

    df_stock = pd.DataFrame()
    df_stock['Entry Price'] = entry_arr
    df_stock['Optimum TP'] = (optimum_tp - df_stock['Entry Price']) / df_stock['Entry Price']
    df_stock['Kitta'] = [applied_units for _ in range(len(df_stock))]
    df_stock['Capital Cost'] = df_stock['Entry Price'] * df_stock['Kitta']
    df_stock['Profit'] = df_stock['Capital Cost'] * df_stock['Optimum TP']

    # Save DataFrame to Excel
    excel_file = io.BytesIO()
    df_stock.to_excel(excel_file, index=False, engine='openpyxl')
    excel_file.seek(0)
    excel_bytes = excel_file.read()
    excel_b64 = base64.b64encode(excel_bytes).decode()

    # Plot
    plt.figure(figsize=(8, 6))
    plt.plot(df_stock['Entry Price'], df_stock['Capital Cost'], label='Cost')
    plt.plot(df_stock['Entry Price'], df_stock['Profit'], label='Profit', c='g')
    plt.title(f"Investment V/S Profit Chart of {applied_units} units")
    plt.axvline(x=125, c='r', label='No Greed Line')
    plt.grid()
    plt.legend()

    # Convert plot to base64
    plot_image = io.BytesIO()
    plt.savefig(plot_image, format='png')
    plot_image.seek(0)
    plot_url = base64.b64encode(plot_image.getvalue()).decode()

    plt.close()

    return df_stock, excel_b64, plot_url

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        df_stock, excel_b64, plot_url = generate_plot()
        return render_template('result.html', tables=[df_stock.to_html(classes='data')], excel_data=excel_b64, plot_url=plot_url)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
