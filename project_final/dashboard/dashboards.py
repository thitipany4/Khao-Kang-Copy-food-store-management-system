#เป็นกราฟ โดย update ทุกๆ 1 นาที
# โดย
import pandas as pd
from dash import dcc, html
from app.models import *
from django_plotly_dash import DjangoDash
import plotly.express as px
from dash.dependencies import Input, Output
from collections import Counter
def call_all():
    app = DjangoDash('AllData')
    food = Food.objects.all()
    foods = [d.name for d in food]
    # print(foods)
    list_dropdown = {food_name: food_name for food_name in foods}

    # Initial layout with data
    app.layout = html.Div([
        dcc.Graph(id='live-update-graph1'),
        dcc.Graph(id='live-update-graph2',className='g3',style={'width':'700px'}),
        dcc.Graph(id='live-update-graph3'),
        html.Div([
            dcc.Dropdown(
                            options=list_dropdown,
                            value=foods[0] ,
                            id='dropdown-column'
                        ),
                dcc.Graph(id='live-update-graph4'),
        ]),
        dcc.Graph(id='live-update-graph5'),
        dcc.Interval(
            id='interval-component',
            interval=60 * 1000,  # in milliseconds
            n_intervals=0
        ),
    ],className='container_dash',style={'padding': '20px','display':'grid','grid-template-columns': 'repeat(2,1fr)',
                                        'grid-gap': '10px','background': 'red','height':'1000px','padding': '0.5rem','margin':' 0.5rem'})
    @app.callback(
                Output('live-update-graph1', 'figure'),
                Output('live-update-graph2', 'figure'),
                Output('live-update-graph3', 'figure'),
                Output('live-update-graph4', 'figure'),
                Output('live-update-graph5', 'figure'),
                Input('dropdown-column', 'value'),
                Input('interval-component', 'n_intervals'),)

    def update_graph(value,n_intervals):
        member = Member.objects.all()
        all_age = [m.age for m in member]
        figure1 = px.pie(names=all_age)
        figure1.update_layout(title='กราฟแสดงเพศของผู้ใช้งาน')

        transaction = Transaction.objects.all()
        price_tran = [t.total_price for t in transaction]
        type_tran = [t.transaction_type for t in transaction]
        date_tran = [str(t.created).split(' ')[0] for t in transaction]
        price_df = pd.DataFrame({'date':date_tran,'price':price_tran,'type':type_tran})
        price_df['year'] = pd.to_datetime(price_df['date']).dt.year
        price_test = price_df.groupby(['year','type'])['price'].sum().reset_index()

        figure2 = px.line(price_test,x='year', y='price',color='type',markers=True)
        figure2.update_layout(
            xaxis_title="วันที่",  
            yaxis_title="ราคา"  ,
            xaxis=dict(
            tickmode='linear', 
            tickvals=price_test['year'].unique() 
        ))

        item1 = OrderItemtype1.objects.all()
        item2 = OrderItemtype2.objects.all()
        list_item = []
        for item in item1:
            list_item.append(item.food.name)
        for item in item2:
            for food in item.foods.all():
                list_item.append(food.name)
        count = Counter(list_item)
        figure3 = px.bar(x=list(count.keys()), y=list(count.values()),color=list(count.keys()), labels={'x': 'ชื่ออาหาร', 'y': 'จำนวนที่ขายได้'})

        foods = Food.objects.all()
        review = Reviewfood.objects.filter(food__name=value)
        rating_dic = {'1':0,'2':0,'3':0,'4':0,'5':0}
        for r in review:
            rating = str(r.rating) 
            if rating in rating_dic:
                rating_dic[rating] += 1
        
        figure4 = px.bar(x=list(rating_dic.values()), y=list(rating_dic.keys()),color=list(rating_dic.keys()), labels={'y': f'คะแนน ({value})', 'x': 'จำนวนที่ขายได้'})
        
        sale = Order.objects.filter(completed='completed')
        order = Order.objects.filter(confirm='cancel')
        print(len(sale),len(order))
        
        merge = sale | order
        age_count_dic = {'ต่ำกว่า 19 ปี':0, '20-39 ปี':0, '40-59 ปี':0, '60 ปีขึ้น':0}
        count_status_dic = {'ต่ำกว่า 19 ปี':[], '20-39 ปี':[], '40-59 ปี':[], '60 ปีขึ้น':[]}

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
        for age, number_saled in age_count_dic.items():
            for status in count_status_dic[age]:
                age_list.append(age)
                status_list.append(status)


        df_order_sale = pd.DataFrame({'age': age_list, 'status': status_list})
        date = [str(s.created_at).split(' ')[0] for s in sale]
        total_price = [s.total_price for s in sale]
        df_complete = pd.DataFrame({'date':date,'price':total_price})
        sort_df_complete = df_complete.groupby('date')['price'].sum().reset_index()
        sort_df_complete['year'] = pd.to_datetime(df_complete['date']).dt.year
        # food = [f.name for f in foods]
        df_count = df_order_sale.groupby(['age', 'status']).size().reset_index(name='count')
        figure5 = px.bar(df_count, x='age', y='count', color='status', barmode='group')

        return figure1,figure2,figure3,figure4,figure5
    
    return app


def call_month(date_filter,list_day):
    app = DjangoDash('MonthData')
    food = Food.objects.all()
    foods = [d.name for d in food]
    # print(foods)
    list_dropdown = {food_name: food_name for food_name in foods}
    app.layout = html.Div([
        dcc.Graph(id='live-update-graph1'),
        dcc.Graph(id='live-update-graph2',className='g3',style={'width':'600px'}),
        dcc.Graph(id='live-update-graph3'),
        html.Div([
            dcc.Dropdown(
                            options=list_dropdown,
                            value=foods[0] ,
                            id='dropdown-column'
                        ),
                dcc.Graph(id='live-update-graph4'),
        ]),
        dcc.Graph(id='live-update-graph5'),
        dcc.Interval(
            id='interval-component',
            interval=60 * 1000,  # in milliseconds
            n_intervals=0
        ),
    ],className='container_dash',style={'padding': '20px','display':'grid','grid-template-columns': 'repeat(2,1fr)',
                                        'grid-gap': '10px','background': 'blue','height':'1000px','padding': '0.5rem','margin':' 0.5rem'})
    @app.callback(
                Output('live-update-graph1', 'figure'),
                Output('live-update-graph2', 'figure'),
                Output('live-update-graph3', 'figure'),
                Output('live-update-graph4', 'figure'),
                Output('live-update-graph5', 'figure'),
                Input('dropdown-column', 'value'),
                Input('interval-component', 'n_intervals'),)

    def update_graph(value,n_intervals):
        #แก้ไขใส่เงื่อนไขว่าถ้า ฐานข้อมูลหาไม่เจอ ให้ รีเทิร์น กราฟว่างไป กราฟ ว่าง สร้าง ได้แบบนี้  px.line()
        
        print('list_day',list_day)
        print(date_filter,'date')

        member = Member.objects.all()
        if member :
            all_age = [m.age for m in member]
            figure1 = px.pie(names=all_age) # ไม่ต้องแก้
            figure1.update_layout(title='กราฟแสดงเพศของผู้ใช้งาน')
        else:
            figure1 = px.pie() # ไม่ต้องแก้
            figure1.update_layout(title='กราฟแสดงเพศของผู้ใช้งาน')

        transaction = Transaction.objects.filter(date__contains=date_filter)
        print(transaction,'transaction 222')
        if transaction:
            date_tran = [str(t.created).split(' ')[0] for t in transaction]
            # print(date_tran)
            price_tran = [t.total_price for t in transaction]
            type_tran = [t.transaction_type for t in transaction]
            price_df = pd.DataFrame({'date':date_tran,'price':price_tran,'type':type_tran})
            price_df['day'] = pd.to_datetime(price_df['date']).dt.day
            price_test = price_df.groupby(['day','type'])['price'].sum().reset_index()

            figure2 = px.line(price_test,x='day', y='price',color='type',markers=True) #แก้ การจัดกลุ่มเป็นวัน และแก้ xickvals 
            figure2.update_layout(
                xaxis_title="วันที่",  
                yaxis_title="ราคา"  ,
                xaxis=dict(
                tickmode='linear', 
                tickvals=list_day
            ))
        else:
            figure2 = px.line()
            figure2.update_layout(
                xaxis_title="วันที่",  
                yaxis_title="ราคา"  ,
                xaxis=dict(
                tickmode='linear', 
                tickvals=list_day
            ))

        order = Order.objects.filter(completed='completed',created_at__contains=date_filter)
        print(order,'order 333')
        if order:
            
            list_item = []
            for o in order:
                item1 = OrderItemtype1.objects.filter(order=o)
                item2 = OrderItemtype2.objects.filter(order=o)
            
                for item in item1:
                    list_item.append(item.food.name)
                for item in item2:
                    for food in item.foods.all():
                        list_item.append(food.name)

            count = Counter(list_item)
            figure3 = px.bar(x=list(count.keys()), y=list(count.values()),color=list(count.keys()), labels={'x': 'ชื่ออาหาร', 'y': 'จำนวนที่ขายได้'}) #แก้ เพิ่ม ลูบ filter order 
        else:
            figure3 = px.bar()

        review = Reviewfood.objects.filter(food__name=value,created__contains=date_filter)
        print(review,'review 444')
        if review:
            rating_dic = {'1':0,'2':0,'3':0,'4':0,'5':0}
            for r in review:
                rating = str(r.rating) 
                if rating in rating_dic:
                    rating_dic[rating] += 1
            # แก้ตรงโมเดลเเล้วได้เลย figure4
            figure4 = px.bar(x=list(rating_dic.values()), y=list(rating_dic.keys()),color=list(rating_dic.keys()), labels={'y': f'คะแนน ({value})', 'x': 'จำนวนที่ขายได้'})
        else:
            figure4 = px.bar()

        completed = Order.objects.filter(completed='completed',created_at__contains=date_filter)
        cancel = Order.objects.filter(confirm='cancel',created_at__contains=date_filter)
        print(completed,'completed 555')
        print(cancel,'cancel 555')

        if  completed or cancel:
            # print('transaction',transaction)
            # foods = Food.objects.all()
            merge = completed | cancel
            age_count_dic = {'ต่ำกว่า 19 ปี':0, '20-39 ปี':0, '40-59 ปี':0, '60 ปีขึ้น':0}
            count_status_dic = {'ต่ำกว่า 19 ปี':[], '20-39 ปี':[], '40-59 ปี':[], '60 ปีขึ้น':[]}

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
            for age, number_saled in age_count_dic.items():
                for status in count_status_dic[age]:
                    age_list.append(age)
                    status_list.append(status)


            df_order_sale = pd.DataFrame({'age': age_list, 'status': status_list})
            date = [str(s.created_at).split(' ')[0] for s in completed]
            total_price = [s.total_price for s in completed]
            df_complete = pd.DataFrame({'date':date,'price':total_price})
            sort_df_complete = df_complete.groupby('date')['price'].sum().reset_index()
            sort_df_complete['year'] = pd.to_datetime(df_complete['date']).dt.year
            df_count = df_order_sale.groupby(['age', 'status']).size().reset_index(name='count')
            figure5 = px.bar(df_count, x='age', y='count', color='status', barmode='group') # 
        else:
            figure5 = px.bar()
        return figure1,figure2,figure3,figure4,figure5
    return app  

def call_quarter(range_date,len_quater):
    app = DjangoDash('QuarterData')
    food = Food.objects.all()
    foods = [d.name for d in food]
    # print(foods)
    list_dropdown = {food_name: food_name for food_name in foods}
    app.layout = html.Div([
        dcc.Graph(id='live-update-graph1'),
        dcc.Graph(id='live-update-graph2',className='g3',style={'width':'600px'}),
        dcc.Graph(id='live-update-graph3'),
        html.Div([
            dcc.Dropdown(
                            options=list_dropdown,
                            value=foods[0] ,
                            id='dropdown-column'
                        ),
                dcc.Graph(id='live-update-graph4'),
        ]),
        dcc.Graph(id='live-update-graph5'),
        dcc.Interval(
            id='interval-component',
            interval=60 * 1000,  # in milliseconds
            n_intervals=0
        ),
    ],className='container_dash',style={'padding': '20px','display':'grid','grid-template-columns': 'repeat(2,1fr)',
                                        'grid-gap': '10px','background': 'blue','height':'1000px','padding': '0.5rem','margin':' 0.5rem'})
    @app.callback(
                Output('live-update-graph1', 'figure'),
                Output('live-update-graph2', 'figure'),
                Output('live-update-graph3', 'figure'),
                Output('live-update-graph4', 'figure'),
                Output('live-update-graph5', 'figure'),
                Input('dropdown-column', 'value'),
                Input('interval-component', 'n_intervals'),)

    def update_graph(value,n_intervals):
        #แก้ไขใส่เงื่อนไขว่าถ้า ฐานข้อมูลหาไม่เจอ ให้ รีเทิร์น กราฟว่างไป กราฟ ว่าง สร้าง ได้แบบนี้  px.line()
        
        print('len_quater',len_quater)
        print(range_date,'date')

        member = Member.objects.all()
        if member :
            all_age = [m.age for m in member]
            figure1 = px.pie(names=all_age) # ไม่ต้องแก้
            figure1.update_layout(title='กราฟแสดงเพศของผู้ใช้งาน')
        else:
            figure1 = px.pie() # ไม่ต้องแก้
            figure1.update_layout(title='กราฟแสดงเพศของผู้ใช้งาน')

        transaction = Transaction.objects.filter(date__range=(range_date))
        if transaction:
            date_tran = [str(t.created).split(' ')[0] for t in transaction]
            # print(date_tran)
            price_tran = [t.total_price for t in transaction]
            type_tran = [t.transaction_type for t in transaction]
            price_df = pd.DataFrame({'date':date_tran,'price':price_tran,'type':type_tran})
            price_df['month'] = pd.to_datetime(price_df['date']).dt.month
            print(price_df)
            price_test = price_df.groupby(['month','type'])['price'].sum().reset_index()

            figure2 = px.line(price_test,x='month', y='price',color='type',markers=True) #แก้ การจัดกลุ่มเป็นวัน และแก้ xickvals 
            figure2.update_layout(
                xaxis_title="วันที่",  
                yaxis_title="ราคา"  ,
                xaxis=dict(
                tickmode='linear', 
                tickvals=len_quater
            ))
        else:
            figure2 = px.line()
            figure2.update_layout(
                xaxis_title="วันที่",  
                yaxis_title="ราคา"  ,
                xaxis=dict(
                tickmode='linear', 
                tickvals=len_quater
            ))

        order = Order.objects.filter(completed='completed',created_at__range=(range_date))
        print(order,'order 333')
        if order:
            
            list_item = []
            for o in order:
                item1 = OrderItemtype1.objects.filter(order=o)
                item2 = OrderItemtype2.objects.filter(order=o)
            
                for item in item1:
                    list_item.append(item.food.name)
                for item in item2:
                    for food in item.foods.all():
                        list_item.append(food.name)

            count = Counter(list_item)
            figure3 = px.bar(x=list(count.keys()), y=list(count.values()),color=list(count.keys()), labels={'x': 'ชื่ออาหาร', 'y': 'จำนวนที่ขายได้'}) #แก้ เพิ่ม ลูบ filter order 
        else:
            figure3 = px.bar()

        review = Reviewfood.objects.filter(food__name=value,created__range=(range_date))
        print(review,'review 444')
        if review:
            rating_dic = {'1':0,'2':0,'3':0,'4':0,'5':0}
            for r in review:
                rating = str(r.rating) 
                if rating in rating_dic:
                    rating_dic[rating] += 1
            # แก้ตรงโมเดลเเล้วได้เลย figure4
            figure4 = px.bar(x=list(rating_dic.values()), y=list(rating_dic.keys()),color=list(rating_dic.keys()), labels={'y': f'คะแนน ({value})', 'x': 'จำนวนที่ขายได้'})
        else:
            figure4 = px.bar()

        completed = Order.objects.filter(completed='completed',created_at__range=(range_date))
        cancel = Order.objects.filter(confirm='cancel',created_at__range=(range_date))
        print(completed,'completed 555')
        print(cancel,'cancel 555')

        if  completed or cancel:
            # print('transaction',transaction)
            # foods = Food.objects.all()
            merge = completed | cancel
            age_count_dic = {'ต่ำกว่า 19 ปี':0, '20-39 ปี':0, '40-59 ปี':0, '60 ปีขึ้น':0}
            count_status_dic = {'ต่ำกว่า 19 ปี':[], '20-39 ปี':[], '40-59 ปี':[], '60 ปีขึ้น':[]}

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
            for age, number_saled in age_count_dic.items():
                for status in count_status_dic[age]:
                    age_list.append(age)
                    status_list.append(status)


            df_order_sale = pd.DataFrame({'age': age_list, 'status': status_list})
            date = [str(s.created_at).split(' ')[0] for s in completed]
            total_price = [s.total_price for s in completed]
            df_complete = pd.DataFrame({'date':date,'price':total_price})
            sort_df_complete = df_complete.groupby('date')['price'].sum().reset_index()
            sort_df_complete['year'] = pd.to_datetime(df_complete['date']).dt.year
            df_count = df_order_sale.groupby(['age', 'status']).size().reset_index(name='count')
            figure5 = px.bar(df_count, x='age', y='count', color='status', barmode='group') # 
        else:
            figure5 = px.bar()
        return figure1,figure2,figure3,figure4,figure5
    return app  

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