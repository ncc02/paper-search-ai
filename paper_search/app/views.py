from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
import csv

PATH = './app/papers_data_done.csv'
URL = './app/image/'

def search_by_keywords(keyword, csv_file_path):
    results = []
    with open(csv_file_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            # Kiểm tra xem từ khóa có trong cột Keywords hay không
            if keyword.lower() in row['Keywords'].lower():
                # Nếu có, thêm hàng vào kết quả
                results.append(row)
    # Sắp xếp kết quả theo cột 'Year' giảm dần
    sorted_results = sorted(results, key=lambda x: int(x['Year']), reverse=True)
    return sorted_results

def search_by_all(keyword, csv_file_path):
    results = []
    with open(csv_file_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            # Duyệt qua tất cả các cột trong hàng và kiểm tra từ khóa trong mỗi cột
            for column, value in row.items():
                if keyword.lower() in str(value).lower():
                    # Nếu có, thêm hàng vào kết quả và dừng vòng lặp cột
                    results.append(row)
                    break
    # Sắp xếp kết quả theo cột 'Year' giảm dần
    sorted_results = sorted(results, key=lambda x: int(x['Year']), reverse=True)
    return sorted_results


@api_view(['GET'])
def search(request):
    text = request.query_params.get('search', 'cnn')  # Lấy tham số search từ query params
    
    search_by = "search_by_keywords"
    search_result = search_by_keywords(text, PATH)
    if search_result == []:
        search_by = "search_by_all"
        search_result = search_by_all(text, PATH)
        
    # Tạo phân trang cho kết quả
    paginator = PageNumberPagination()
    paginated_search_result = paginator.paginate_queryset(search_result, request)

    # Tạo dictionary chứa thông tin phân trang và kết quả tìm kiếm
    response_data = {
        'search_by' : search_by,
        'count': paginator.page.paginator.count,  # Tổng số mục
        'next': paginator.get_next_link(),        # Link tới trang kế tiếp (nếu có)
        'previous': paginator.get_previous_link(),# Link tới trang trước đó (nếu có)
        'results': paginated_search_result        # Kết quả tìm kiếm
    }

    # Trả về phản hồi RESTful API
    return Response(response_data, status=200)



import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt

from wordcloud import WordCloud
from datetime import datetime

@api_view(['GET'])
def trend_year(request):
    year = request.query_params.get('year', '') # Lấy tham số search từ query params
    if year == '':
        year = datetime.now().year - 1

    url, table = get_url_table(int(year))
    response_data = {
        "url": url,
        "table": table,
    }    
    # Trả về phản hồi RESTful API
    return Response(response_data, status=200)

def get_url_table(year):
    df = pd.read_csv(PATH)  
    data_for_year = df[df['Year'] == year]
    dic = {}
    for data in data_for_year.Keywords:
        # Loại bỏ dấu ngoặc đơn và dấu phẩy ở đầu và cuối chuỗi
        string = data.strip("[]")

        # Tách chuỗi thành các từ dựa trên dấu phẩy và khoảng trắng
        words = string.split(", ")
        for word in words:
            if word[1:-1] not in dic:
                dic[word[1:-1]] = 1
            else:
                dic[word[1:-1]] += 1
    
    if "" in dic:
        dic[""] = 0

    

    # Chuyển dictionary thành DataFrame
    df_table = pd.DataFrame(dic.items(), columns=['Word', 'Frequency'])

    # Sắp xếp theo tần suất giảm dần
    df_table = df_table.sort_values(by='Frequency', ascending=False)

    # Lấy 20 từ xuất hiện nhiều nhất
    top_20_words = df_table.head(20)

    # Tạo một dictionary từ DataFrame top_20_words
    word_freq_dict = dict(zip(top_20_words['Word'], top_20_words['Frequency']))
    
    # Tạo word cloud object
    wordcloud = WordCloud(width=800, height=400, background_color ='white').generate_from_frequencies(word_freq_dict)

    # Hiển thị word cloud
    plt.figure(figsize=(10, 8))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    
    # Lưu sơ đồ wordcloud vào file ảnh
    image_path = URL + 'wordcloud.png'
    plt.savefig(image_path)
    return image_path, top_20_words
  
@api_view(['GET'])
def trend_10_year(request):
    year = request.query_params.get('year', '') # Lấy tham số search từ query params
    if year == '':
        year = datetime.now().year - 1
    else:
        year = int(year)
    
    # Đọc dữ liệu từ tệp CSV
    df = pd.read_csv(PATH)
    
    # Tạo một danh sách để lưu trữ dữ liệu từ khóa và tần suất
    keyword_data_list = []
    
    # Lặp qua từng năm từ 9 năm trước đến năm hiện tại
    for y in range(max(1987, year - 9), year + 1):
        # Lọc dữ liệu cho từng năm
        data_for_year = df[df['Year'] == y]
        
        # Tạo một từ điển để đếm tần suất của từng từ khóa cho năm hiện tại
        keyword_count = {}
        for keywords in data_for_year['Keywords']:
            # Xử lý chuỗi từ khóa và đếm tần suất xuất hiện của từng từ khóa
            words = keywords.strip('[]').split(', ')
            for word in words:
                word = word.strip("'")
                keyword_count[word] = keyword_count.get(word, 0) + 1
        
        # Thêm dữ liệu từ khóa và tần suất vào danh sách
        for keyword, freq in keyword_count.items():
            keyword_data_list.append({'Year': y, 'Keyword': keyword, 'Frequency': freq})
    
    # Tạo DataFrame từ danh sách dữ liệu từ khóa
    keyword_trends = pd.DataFrame(keyword_data_list)
    # Lấy top 10 từ khóa phổ biến nhất
    top_10_keywords = keyword_trends.groupby('Keyword').sum()['Frequency'].nlargest(10).index
    
    # Lọc dữ liệu cho top 10 từ khóa
    for keyword in top_10_keywords:
        keyword_data = keyword_trends[keyword_trends['Keyword'] == keyword]
        
        # Tạo biểu đồ đường cho từng từ khóa
        plt.plot(keyword_data['Year'], keyword_data['Frequency'], label=keyword)

    # Đặt tiêu đề và nhãn cho biểu đồ
    plt.title('Trend of Top 10 Keywords Over 10 Years')
    plt.xlabel('Year')
    plt.ylabel('Frequency')
    plt.legend()
    
    # Lưu biểu đồ dưới dạng ảnh
    image_path = URL + 'line_graph.png'
    plt.savefig(image_path)
    plt.close()  # Đóng biểu đồ để giải phóng bộ nhớ
    
    response_data = {
        "url": image_path,
    }    
    # Trả về phản hồi RESTful API
    return Response(response_data, status=200)