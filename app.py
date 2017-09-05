from flask import Flask, render_template, request, redirect
import datetime as dt
import requests
import pandas as pd
import bokeh
from bokeh.plotting import figure

#------------------------------------------------------------------

def read_api_key(filename='quandl_API_KEY.txt'):
	with open(filename, 'r') as fh:
		for line in fh:
			return line.rstrip()

#------------------------------------------------------------------

def fetch_quandl(ticker, api_key, period=30):
    
	ticker = ticker.upper()                     # API only recognizes uppercase tickers
    
	end = dt.datetime.now()
	start = end - dt.timedelta(days=period)
	end = end.strftime("%Y-%m-%d")              #   API takes dates in yyyy-mm-dd format
	start = start.strftime("%Y-%m-%d")
    
	url = 'https://www.quandl.com/api/v3/datasets/WIKI/' + \
          ticker + '.json?start_date=' + start + '&end_date=' + end + \
          '&api_key=' + api_key
            
	r = requests.get(url)
	if r.status_code == requests.codes.ok:
		data = r.json()['dataset']
		df = pd.DataFrame(columns=data['column_names'], data=data['data'])
		df = df.set_index(pd.DatetimeIndex(df['Date']))
        
	else:
		print('Error! Fetching failed for ticker %s.' %(ticker))
		df = None
	        
	return df

#------------------------------------------------------------------

def plot_data(df, column_name, ticker):

	ticker = ticker.upper()
	
	plot = figure(x_axis_type='datetime', width=800, height=600)
	plot.title.text = column_name + ' price for ' + ticker
	plot.title.text_font_size='20pt'
	plot.background_fill_color = "beige"
	plot.background_fill_alpha = 0.5

	plot.line(df.index, df[column_name], line_width=3)
	plot.circle(df.index, df[column_name], size=15, alpha=0.5)

	plot.xaxis.axis_label = 'Date'
	plot.xaxis.axis_label_text_font_size = "20pt"
	plot.yaxis.axis_label = 'Price ($)'
	plot.yaxis.axis_label_text_font_size = "20pt"

	bokeh.io.output_file('templates/plot.html')
	bokeh.io.save(plot)

	script, div = bokeh.embed.components(plot)

	return script, div
#------------------------------------------------------------------

app = Flask(__name__)

api_key = read_api_key()

@app.route('/')
def main():
	return redirect('/index')

@app.route('/index', methods=['GET','POST'])
def index():
	return render_template('index.html')

@app.route('/resultpage', methods=['GET', 'POST'])
def result_page():

	ticker = request.form['stock']
	column_name = request.form['feature']
	
	df = fetch_quandl(ticker, api_key)
	
	if not type(df) == pd.DataFrame:
		msg = "Wrong ticker name, please try again."
		return render_template('index.html', msg=msg)

	else:
		script, div = plot_data(df, column_name, ticker)
		return render_template('plot.html', script=script, div=div)	

if __name__ == '__main__':
	#app.debug = True
	app.run(port=33508)
