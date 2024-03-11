#เป็นกราฟ โดย update ทุกๆ 1 นาที
# โดย
import pandas as pd
from dash import dcc, html
from app.models import *
from django_plotly_dash import DjangoDash
import plotly.express as px
from dash.dependencies import Input, Output
from collections import Counter

app = DjangoDash('SimpleExample')
food = Food.objects.all()
foods = [d.name for d in food]
print(foods)
list_dropdown = {food_name: food_name for food_name in foods}

# Initial layout with data
app.layout = html.Div([
    html.Div(children='My First App with Data and a Graph', className='header',style={'color':'blue'}),
    dcc.Graph(id='live-update-graph1'),
    dcc.Graph(id='live-update-graph2'),
    dcc.Graph(id='live-update-graph3',className='g3',style={'width':'700px'}),
    dcc.Graph(id='live-update-graph4'),
    html.Div([
        dcc.Dropdown(
                        options=list_dropdown,
                        value=foods[0] ,
                        id='dropdown-column'
                    ),
            dcc.Graph(id='live-update-graph5'),
    ]),
    dcc.Graph(id='live-update-graph6'),
    dcc.Interval(
        id='interval-component',
        interval=60 * 1000,  # in milliseconds
        n_intervals=0
    ),
],className='container_dash',style={'padding': '20px','display':'grid','grid-template-columns': 'repeat(2,1fr)',
                                    'grid-gap': '10px','background': 'red','height':'1500px','padding': '0.5rem','margin':' 0.5rem'})
@app.callback(
             Output('live-update-graph1', 'figure'),
             Output('live-update-graph2', 'figure'),
             Output('live-update-graph3', 'figure'),
             Output('live-update-graph4', 'figure'),
             Output('live-update-graph5', 'figure'),
             Output('live-update-graph6', 'figure'),
             Input('dropdown-column', 'value'),
             Input('interval-component', 'n_intervals'),)

def update_graph(value,n_intervals):
    sale = Order.objects.filter(completed='completed')
    order = Order.objects.filter(confirm='cancel')
    transaction = Transaction.objects.all()
    item1 = OrderItemtype1.objects.all()
    item2 = OrderItemtype2.objects.all()
    foods = Food.objects.all()
    review = Reviewfood.objects.filter(food__name=value)
    list_item = []
    for item in item1:
        list_item.append(item.food.name)
    for item in item2:
        for food in item.foods.all():
            list_item.append(food.name)
    count = Counter(list_item)
    # print(count)

    member = Member.objects.all()
    all_age = [m.age for m in member]
    merge = sale | order
    age_count_dic = {'11-20 ปี': 0, '21-30 ปี': 0, '31-40 ปี': 0, '41-50 ปี': 0, '51-60 ปี': 0, '60 ปีขึ้น': 0}
    count_status_dic = {'11-20 ปี': [], '21-30 ปี': [], '31-40 ปี': [], '41-50 ปี': [], '51-60 ปี': [], '60 ปีขึ้น': []}

    for m in merge:
        member_order = Member.objects.get(user=m.user)
        member_age = str(member_order.age)
        if member_age in age_count_dic:
            age_count_dic[member_age] += 1
            if m.completed == 'completed':
                count_status_dic[member_age].append('completed')
            if m.confirm == 'cancel':
                count_status_dic[member_age].append('cancel')

    age_list = []
    status_list = []
    count_list =[]
    for age, number_saled in age_count_dic.items():
        for status in count_status_dic[age]:
            age_list.append(age)
            status_list.append(status)


    df_order_sale = pd.DataFrame({'age': age_list, 'status': status_list})
    print(df_order_sale)

    date = [s.created_at for s in sale]
    total_price = [s.total_price for s in sale]
    date_tran = [t.created for t in transaction]
    price_tran = [t.total_price for t in transaction]
    type_tran = [t.transaction_type for t in transaction]
    food = [f.name for f in foods]
    rating_dic = {'1':0,'2':0,'3':0,'4':0,'5':0}
    for r in review:
        rating = str(r.rating) 
        if rating in rating_dic:
            rating_dic[rating] += 1

    print(rating_dic)
    
    print(rating)
    
    figure1 = px.pie(names=all_age)
    figure2 = px.line(x=date, y=total_price,markers=True)
    figure2.update_layout(
        xaxis_title="Date",  
        yaxis_title="Total Price"  
    )
    figure3 = px.line(x=date_tran, y=price_tran,color=type_tran,markers=True)
    figure3.update_layout(
        xaxis_title="วันที่",  
        yaxis_title="ราคา"  
    )
    figure4 = px.bar(x=list(count.keys()), y=list(count.values()),color=list(count.keys()), labels={'x': 'ชื่ออาหาร', 'y': 'จำนวนที่ขายได้'})
    figure5 = px.bar(x=list(rating_dic.values()), y=list(rating_dic.keys()),color=list(rating_dic.keys()), labels={'y': f'คะแนน ({value})', 'x': 'จำนวนที่ขายได้'})
    df_count = df_order_sale.groupby(['age', 'status']).size().reset_index(name='count')
    figure6 = px.bar(df_count, x='age', y='count', color='status', barmode='group')
    return figure1,figure2,figure3,figure4,figure5,figure6
    
'''
กราฟที่คิดจะทำได้ 
1 Histogram การกระจายของ อายุ
2 Pie Chart สำหรับการกระจายเพศ
3 Line Plot สำหรับปริมาณอาหารที่ขายตามเวลา
4 Line Plot สำหรับปริมาณรายรับรายจ่าย เปลี่ยน x ให้เป็นจำนวนวันของเดือนั้น
5 Bar Chart สำหรับการรีวิว 

กราฟที่ต้องทำ
รายรับ รายจ่าย เป็นตัวเลข แสดงว่สเท่าไร โดยรวม เปรียบเทียบกับของเดือนก่อนด้วย

'''