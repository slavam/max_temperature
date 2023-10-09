import gradio as gr
import numpy as np
import tensorflow as tf
from datetime import datetime
import time
# import ipywidgets as widgets
# from ipywidgets import VBox

def prepare_data(telegram):
  ret = []
  ret.append(int(telegram[18:19])) # cloud_amount
  sign = ''
  if telegram[25:26] == '1':
    sign = '-'
  ret.append(float(sign+telegram[26:28]+'.'+telegram[28:29]))# temperature
  sign = ''
  if telegram[31:32] == '1':
    sign = '-'
  ret.append(float(sign+telegram[32:34]+'.'+telegram[34:35]))# temperature_dew
  p1 = '1'
  if telegram[37:38] != '0':
    p1 = ''
  ret.append(float(p1+telegram[37:40]+'.'+telegram[40:41]))# pressure
  ret.append(float(telegram[49:50]+'.'))#  pressure_tendency
  ret.append(float(telegram[50:52]+'.'+telegram[52:53]))# pressure_tendency_value
  wv = float(telegram[21:23]+'.')
  wd_rad = int(telegram[19:21])*10*np.pi/180
  ret.append(wv*np.cos(wd_rad)) # Wx
  ret.append(wv*np.sin(wd_rad)) # Wy
  now = datetime.utcnow()
  date_term = now.strftime('%Y-%m-%d')
  date_term += ' '+"{:02d}".format(int(now.hour / 3) * 3)+':00:00'
  d = datetime.strptime(date_term, "%Y-%m-%d %H:%M:%S")
  s = time.mktime(d.timetuple())
  day = 24*60*60
  year = (365.2425)*day
  ret.append(np.sin(s * (2 * np.pi / day)))
  ret.append(np.cos(s * (2 * np.pi / day)))
  ret.append(np.sin(s * (2 * np.pi / year)))
  ret.append(np.cos(s * (2 * np.pi / year))) #Day sin 	Day cos 	Year sin 	Year cos
  telegram = [ret]
  model = tf.keras.models.load_model('improve_dnn_model_3')
  predict_temperature = model.predict(telegram).flatten()[0]
  
  return predict_temperature


#telegram = widgets.Text(
#    value='',
#    placeholder='05061 34519 11597 60000 10126 20100 39970 40212 53005 69962 72581 86500 333 20113 555 53004=',
#    description='Последняя телеграмма:',
#    disabled=False,
#    style={'description_width': 'initial'},
#    layout = widgets.Layout(width='800px')
#)
#def on_click_classify(change):
#    max_temperature = prepare_data(d_t, telegram.value)
#    lbl_pred.value = f'Максимальная температура в Донецке {d_t[:10]} ожидается {str(round(max_temperature,2))}'
#btn_run = widgets.Button(description='Сделать прогноз')
#btn_run.on_click(on_click_classify)
#lbl_pred = widgets.Label()
#VBox([widgets.Label('Прогноз махсимальной температуры в Донецке'), telegram, btn_run, lbl_pred])

# def greet(name):
#    return "Hello " + name + "!!!"
title = "Прогноз максимальной суточной температуры воздуха в Донецке"
description = "Прогноз делается на основании синоптической телеграммы за текущий срок"

iface = gr.Interface(fn=prepare_data, inputs="text", outputs="text",title=title,description=description)
iface.launch()
