import streamlit as st
import akshare as ak
import pandas as pd
import time
from datetime import datetime, date

def get_stock_data(max_retries=3, delay=2):
    """获取股票数据，带重试机制"""
    for attempt in range(max_retries):
        try:
            with st.spinner('正在获取股票数据...'):
                stock_list = ak.stock_zh_a_spot_em()
            return stock_list
        except Exception as e:
            if attempt < max_retries - 1:
                st.warning(f"第 {attempt + 1} 次尝试失败，{delay} 秒后重试...")
                time.sleep(delay)
            else:
                st.error(f"获取数据失败: {str(e)}")
                raise

def get_limit_up_stocks(trade_date, max_retries=3, delay=2):
    """获取涨停板信息"""
    for attempt in range(max_retries):
        try:
            with st.spinner('正在获取涨停板数据...'):
                df = ak.stock_zt_pool_em(date=trade_date)
            return df
        except Exception as e:
            if attempt < max_retries - 1:
                st.warning(f"第 {attempt + 1} 次尝试失败，{delay} 秒后重试...")
                time.sleep(delay)
            else:
                st.error(f"获取涨停板数据失败: {str(e)}")
                raise

def get_limit_down_stocks(trade_date, max_retries=3, delay=2):
    """获取跌停板信息"""
    for attempt in range(max_retries):
        try:
            with st.spinner('正在获取跌停板数据...'):
                df = ak.stock_zt_pool_dtgc_em(date=trade_date)
            return df
        except Exception as e:
            if attempt < max_retries - 1:
                st.warning(f"第 {attempt + 1} 次尝试失败，{delay} 秒后重试...")
                time.sleep(delay)
            else:
                st.error(f"获取跌停板数据失败: {str(e)}")
                raise

def filter_stocks(stock_list, pe_max, pb_max, wave_threshold):
    """根据条件筛选股票"""
    return stock_list[
        ((stock_list['涨跌幅'] > wave_threshold) | (stock_list['涨跌幅'] < -wave_threshold)) & 
        (stock_list['市盈率-动态'] < pe_max) & 
        (stock_list['市净率'] < pb_max) & 
        (stock_list['市盈率-动态'] > 0) & 
        (stock_list['市净率'] > 0)
    ]

def main():
    st.title('A股股票筛选器')
    
    # 创建选项卡
    tab1, tab2, tab3 = st.tabs(["股票筛选", "涨停板", "跌停板"])
    
    with tab1:
        # 侧边栏参数设置
        st.sidebar.header('筛选参数设置')
        pe_max = st.sidebar.slider('最大市盈率', 0.0, 100.0, 25.0)
        pb_max = st.sidebar.slider('最大市净率', 0.0, 10.0, 2.5)
        wave_threshold = st.sidebar.slider('波动幅度阈值(%)', 0.0, 10.0, 4.6)
        
        # 添加刷新按钮
        if st.button('获取最新数据', key='refresh_main'):
            try:
                # 获取股票数据
                stock_list = get_stock_data()
                
                # 筛选股票
                filtered_stocks = filter_stocks(stock_list, pe_max, pb_max, wave_threshold)
                
                # 显示结果
                st.success(f'符合条件的股票数量: {len(filtered_stocks)}')
                
                # 显示筛选结果
                if not filtered_stocks.empty:
                    st.dataframe(filtered_stocks)
                    
                    # 添加下载按钮
                    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
                    csv = filtered_stocks.to_csv(index=False, encoding='utf-8')
                    st.download_button(
                        label="下载筛选结果",
                        data=csv,
                        file_name=f'stock_analysis_{current_time}.csv',
                        mime='text/csv'
                    )
                else:
                    st.info('没有找到符合条件的股票')
            except Exception as e:
                st.error(f'发生错误: {str(e)}')
    
    with tab2:
        # 涨停板数据
        st.header('涨停板数据')
        trade_date = st.date_input(
            "选择交易日期",
            date.today(),
            key='limit_up_date'
        )
        if st.button('获取涨停数据', key='refresh_limit_up'):
            try:
                limit_up_df = get_limit_up_stocks(trade_date.strftime("%Y%m%d"))
                if not limit_up_df.empty:
                    st.success(f'涨停股票数量: {len(limit_up_df)}')
                    st.dataframe(limit_up_df)
                    
                    # 添加下载按钮
                    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
                    csv = limit_up_df.to_csv(index=False, encoding='utf-8')
                    st.download_button(
                        label="下载涨停数据",
                        data=csv,
                        file_name=f'limit_up_{trade_date}_{current_time}.csv',
                        mime='text/csv'
                    )
                else:
                    st.info('没有找到涨停股票')
            except Exception as e:
                st.error(f'发生错误: {str(e)}')
    
    with tab3:
        # 跌停板数据
        st.header('跌停板数据')
        trade_date = st.date_input(
            "选择交易日期",
            date.today(),
            key='limit_down_date'
        )
        if st.button('获取跌停数据', key='refresh_limit_down'):
            try:
                limit_down_df = get_limit_down_stocks(trade_date.strftime("%Y%m%d"))
                if not limit_down_df.empty:
                    st.success(f'跌停股票数量: {len(limit_down_df)}')
                    st.dataframe(limit_down_df)
                    
                    # 添加下载按钮
                    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
                    csv = limit_down_df.to_csv(index=False, encoding='utf-8')
                    st.download_button(
                        label="下载跌停数据",
                        data=csv,
                        file_name=f'limit_down_{trade_date}_{current_time}.csv',
                        mime='text/csv'
                    )
                else:
                    st.info('没有找到跌停股票')
            except Exception as e:
                st.error(f'发生错误: {str(e)}')
    
    # 添加说明信息
    with st.expander("使用说明"):
        st.write("""
        - 本程序用于筛选 A 股市场中符合特定条件的股票
        - 市盈率（PE）：反映股票的估值水平
        - 市净率（PB）：反映公司的账面价值
        - 波动幅度：当日股价涨跌幅的绝对值
        - 涨停板/跌停板：显示当日涨停/跌停的股票信息
        - 可以通过侧边栏调整筛选参数
        - 所有数据都可以导出为 CSV 文件
        """)

if __name__ == '__main__':
    main() 
