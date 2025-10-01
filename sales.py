# Enhanced Retail Sales & Profitability Analysis Dashboard
# Requirements: streamlit, pandas, numpy, plotly, prophet, openpyxl

import pandas as pd
import numpy as np
import streamlit as st
import warnings
import io
warnings.filterwarnings('ignore')

# Import with error handling for cloud deployment
try:
    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError as e:
    st.error(f"Plotly import failed: {e}")
    PLOTLY_AVAILABLE = False

try:
    from prophet import Prophet
    PROPHET_AVAILABLE = True
except ImportError as e:
    st.error(f"Prophet import failed: {e}")
    PROPHET_AVAILABLE = False

# Page configuration
st.set_page_config(
    page_title="Retail Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .stMetric > label {
        font-size: 14px !important;
        font-weight: 600 !important;
    }
    .stMetric > div {
        font-size: 24px !important;
        font-weight: 700 !important;
    }
    .upload-section {
        background-color: #1e1e1e;
        padding: 2rem;
        border-radius: 10px;
        margin: 1rem 0;
        border: 2px dashed #444;
    }
    .upload-icon {
        font-size: 3rem;
        color: #666;
        margin-bottom: 1rem;
    }
    .upload-text {
        color: #ccc;
        font-size: 1.1rem;
        margin-bottom: 0.5rem;
    }
    .upload-subtext {
        color: #888;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# Required columns for Global Superstore format
REQUIRED_COLUMNS = [
    'Order Date', 'Ship Date', 'Category', 'Sub-Category', 
    'Product Name', 'Sales', 'Discount', 'Profit', 'Quantity'
]

def validate_dataset(df):
    """Validate that the uploaded dataset has the required structure"""
    missing_columns = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    
    if missing_columns:
        return False, f"Missing required columns: {', '.join(missing_columns)}"
    
    # Check data types
    try:
        pd.to_datetime(df['Order Date'])
        pd.to_datetime(df['Ship Date'])
    except:
        return False, "Order Date and Ship Date must be valid date formats"
    
    # Check numeric columns
    numeric_columns = ['Sales', 'Discount', 'Profit', 'Quantity']
    for col in numeric_columns:
        if not pd.api.types.is_numeric_dtype(df[col]):
            return False, f"Column '{col}' must contain numeric values"
    
    return True, "Dataset validation successful"

def create_file_upload_component():
    """Create the file upload component"""
    st.markdown('<div class="upload-section">', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="upload-icon">☁️</div>', unsafe_allow_html=True)
        st.markdown('<div class="upload-text">Upload Excel file (.xlsx only)</div>', unsafe_allow_html=True)
        st.markdown('<div class="upload-subtext">Drag and drop file here</div>', unsafe_allow_html=True)
        st.markdown('<div class="upload-subtext">Limit 200MB per file • XLSX</div>', unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=['xlsx'],
        help="Upload a dataset with the same structure as Global Superstore",
        label_visibility="collapsed"
    )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    return uploaded_file

def load_uploaded_data(uploaded_file):
    """Load and validate uploaded data"""
    if uploaded_file is not None:
        # Show loading spinner for file processing
        with st.spinner("📁 Reading Excel file..."):
            try:
                # Read the Excel file
                df = pd.read_excel(uploaded_file)
                
                # Show progress for validation
                with st.spinner("🔍 Validating dataset structure..."):
                    # Validate the dataset
                    is_valid, message = validate_dataset(df)
                
                if is_valid:
                    # Show progress for date conversion
                    with st.spinner("📅 Converting date formats..."):
                        try:
                            df['Order Date'] = pd.to_datetime(df['Order Date'])
                            df['Ship Date'] = pd.to_datetime(df['Ship Date'])
                            
                            # Show success with data summary
                            st.success("✅ Dataset uploaded and validated successfully!")
                            
                            # Display data summary
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Total Records", f"{len(df):,}")
                            with col2:
                                st.metric("Date Range", f"{df['Order Date'].min().strftime('%Y-%m-%d')} to {df['Order Date'].max().strftime('%Y-%m-%d')}")
                            with col3:
                                st.metric("Categories", f"{df['Category'].nunique()}")
                            
                            return df
                        except Exception as date_error:
                            st.error(f"❌ Error converting dates: {str(date_error)}")
                            return None
                else:
                    st.error(f"❌ Dataset validation failed: {message}")
                    st.info("Required columns: " + ", ".join(REQUIRED_COLUMNS))
                    return None
                    
            except Exception as e:
                st.error(f"❌ Error reading file: {str(e)}")
                return None
    
    return None


def calculate_kpis(df):
    """Calculate key performance indicators"""
    total_sales = df['Sales'].sum()
    total_profit = df['Profit'].sum()
    profit_margin = (total_profit / total_sales) * 100 if total_sales > 0 else 0
    avg_order_value = df['Sales'].mean()
    total_orders = len(df)
    
    return {
        'total_sales': total_sales,
        'total_profit': total_profit,
        'profit_margin': profit_margin,
        'avg_order_value': avg_order_value,
        'total_orders': total_orders
    }

def create_sales_forecast(df, periods=90):
    """Create sales forecast using Prophet"""
    if not PROPHET_AVAILABLE:
        st.error("❌ Prophet is not available. Forecasting disabled.")
        return None, None
    
    # Prepare data for Prophet
    sales_data = df.groupby('Order Date')['Sales'].sum().reset_index()
    sales_data = sales_data.rename(columns={'Order Date': 'ds', 'Sales': 'y'})
    
    # Fit Prophet model
    model = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=True,
        daily_seasonality=False
    )
    model.fit(sales_data)
    
    # Make future predictions
    future = model.make_future_dataframe(periods=periods)
    forecast = model.predict(future)
    
    return sales_data, forecast

def main():
    st.title("📊 Retail Sales & Profitability Analysis")
    st.markdown("---")
    
    # File upload section
    st.subheader("📁 Data Upload")
    uploaded_file = create_file_upload_component()
    
    # Only show analysis if a file is uploaded
    if uploaded_file is not None:
        df = load_uploaded_data(uploaded_file)
        
        if df is not None and not df.empty:
            # Show analysis only after successful upload
            show_analysis(df)
        else:
            st.error("❌ Please upload a valid dataset to see the analysis.")
    else:
        # Show upload instructions when no file is uploaded
        st.info("📋 Please upload an Excel file (.xlsx) with the same structure as Global Superstore to begin analysis.")
        st.markdown("""
        **Required columns in your dataset:**
        - Order Date, Ship Date, Category, Sub-Category
        - Product Name, Sales, Discount, Profit, Quantity
        """)
        
        # Show sample data structure
        with st.expander("📊 View Sample Data Structure"):
            sample_data = {
                'Order Date': ['2023-01-01', '2023-01-02', '2023-01-03'],
                'Ship Date': ['2023-01-02', '2023-01-03', '2023-01-04'],
                'Category': ['Technology', 'Furniture', 'Office Supplies'],
                'Sub-Category': ['Phones', 'Chairs', 'Binders'],
                'Product Name': ['iPhone 14', 'Office Chair', 'Binder Clips'],
                'Sales': [999.99, 299.99, 15.99],
                'Discount': [0.1, 0.0, 0.05],
                'Profit': [199.99, 59.99, 3.19],
                'Quantity': [1, 1, 5]
            }
            st.dataframe(pd.DataFrame(sample_data), use_container_width=True)

def show_analysis(df):
    """Display the complete analysis dashboard for uploaded data"""
    st.success("✅ Data uploaded successfully! Here's your analysis:")
    
    # Create progress bar for overall analysis
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Show loading for data processing
    with st.spinner("🔄 Processing data for analysis..."):
        status_text.text("🔄 Initializing analysis...")
        progress_bar.progress(10)
        
        # Ensure dates are properly converted
        try:
            df['Order Date'] = pd.to_datetime(df['Order Date'])
            df['Ship Date'] = pd.to_datetime(df['Ship Date'])
            progress_bar.progress(20)
        except Exception as e:
            st.error(f"❌ Error converting dates: {str(e)}")
            return
    
    # Sidebar filters
    st.sidebar.header("Filters")
    
    # Date filter with proper date conversion
    try:
        min_date = df['Order Date'].min().date()
        max_date = df['Order Date'].max().date()
        
        date_range = st.sidebar.date_input(
            "Select Date Range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )
    except Exception as e:
        st.error(f"❌ Error setting up date filter: {str(e)}")
        return
    
    # Category filter
    categories = st.sidebar.multiselect(
        "Select Categories",
        options=df['Category'].unique(),
        default=df['Category'].unique()
    )
    
    # Filter data
    filtered_df = df[
        (df['Order Date'].dt.date >= date_range[0]) &
        (df['Order Date'].dt.date <= date_range[1]) &
        (df['Category'].isin(categories))
    ]
    
    # Calculate KPIs with loading indicator
    status_text.text("📊 Calculating key performance indicators...")
    progress_bar.progress(30)
    
    with st.spinner("📊 Calculating key performance indicators..."):
        kpis = calculate_kpis(filtered_df)
    
    # Display KPIs
    st.subheader("Key Performance Indicators")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            "Total Sales",
            f"₹{kpis['total_sales']:,.0f}",
            delta=f"{kpis['profit_margin']:.1f}% margin"
        )
    
    with col2:
        st.metric(
            "Total Profit",
            f"₹{kpis['total_profit']:,.0f}"
        )
    
    with col3:
        st.metric(
            "Profit Margin",
            f"{kpis['profit_margin']:.1f}%"
        )
    
    with col4:
        st.metric(
            "Avg Order Value",
            f"₹{kpis['avg_order_value']:.0f}"
        )
    
    with col5:
        st.metric(
            "Total Orders",
            f"{kpis['total_orders']:,}"
        )
    
    st.markdown("---")
    
    # Charts section with loading indicators
    st.subheader("📈 Data Visualizations")
    status_text.text("📊 Generating sales and profit charts...")
    progress_bar.progress(50)
    
    with st.spinner("📊 Generating sales and profit charts..."):
        col1, col2 = st.columns(2)
        
    with col1:
        st.subheader("Sales Over Time")
        daily_sales = filtered_df.groupby('Order Date')['Sales'].sum().reset_index()
        
        if PLOTLY_AVAILABLE:
            fig_sales = px.line(
                daily_sales,
                x='Order Date',
                y='Sales',
                title="Daily Sales Trend",
                labels={'Sales': 'Sales (₹)', 'Order Date': 'Date'}
            )
            fig_sales.update_layout(height=400)
            st.plotly_chart(fig_sales, use_container_width=True)
        else:
            st.error("❌ Plotly not available. Charts disabled.")
            st.dataframe(daily_sales)
        
        with col2:
            st.subheader("Profit by Category")
            category_profit = filtered_df.groupby('Category')['Profit'].sum().reset_index()
            fig_category = px.bar(
                category_profit,
                x='Category',
                y='Profit',
                title="Profit by Category",
                color='Profit',
                color_continuous_scale='RdYlGn'
            )
            fig_category.update_layout(height=400)
            st.plotly_chart(fig_category, use_container_width=True)
    
    # Second row of charts with loading indicators
    status_text.text("📊 Generating advanced analytics charts...")
    progress_bar.progress(70)
    
    with st.spinner("📊 Generating advanced analytics charts..."):
        col3, col4 = st.columns(2)
        
        with col3:
            st.subheader("Discount Impact Analysis")
            discount_impact = filtered_df.groupby('Discount').agg({
                'Profit': 'mean',
                'Sales': 'mean'
            }).reset_index()
            
            fig_discount = px.scatter(
                filtered_df,
                x='Discount',
                y='Profit',
                color='Category',
                size='Sales',
                title="Discount vs Profit Analysis",
                labels={'Discount': 'Discount Rate', 'Profit': 'Profit (₹)'}
            )
            fig_discount.update_layout(height=400)
            st.plotly_chart(fig_discount, use_container_width=True)
        
        with col4:
            st.subheader("Top/Bottom Products")
            product_analysis = filtered_df.groupby('Product Name')['Profit'].sum().reset_index()
            
            # Toggle between top and bottom products
            view_type = st.radio("View:", ["Top 10 Profitable", "Bottom 10 Products"], horizontal=True)
            
            if view_type == "Top 10 Profitable":
                top_products = product_analysis.nlargest(10, 'Profit')
                color_scale = 'Greens'
            else:
                top_products = product_analysis.nsmallest(10, 'Profit')
                color_scale = 'Reds'
            
            # Truncate long product names
            top_products['Short Name'] = top_products['Product Name'].str[:30] + '...'
            
            fig_products = px.bar(
                top_products,
                x='Profit',
                y='Short Name',
                orientation='h',
                title=f"{view_type}",
                color='Profit',
                color_continuous_scale=color_scale
            )
            fig_products.update_layout(height=400)
            st.plotly_chart(fig_products, use_container_width=True)
    
    # Sales Forecasting Section
    st.markdown("---")
    st.subheader("Sales Forecasting")
    
    col_forecast1, col_forecast2 = st.columns([2, 1])
    
    with col_forecast2:
        forecast_days = st.slider("Forecast Days", 30, 180, 90, 30)
        show_components = st.checkbox("Show Forecast Components")
    
    with col_forecast1:
        status_text.text("🔮 Generating sales forecast using Prophet AI...")
        progress_bar.progress(85)
        
        with st.spinner("🔮 Generating sales forecast using Prophet AI..."):
            sales_data, forecast = create_sales_forecast(filtered_df, forecast_days)
        
        # Create forecast visualization
        fig_forecast = go.Figure()
        
        # Historical data
        fig_forecast.add_trace(go.Scatter(
            x=sales_data['ds'],
            y=sales_data['y'],
            mode='lines',
            name='Historical Sales',
            line=dict(color='blue')
        ))
        
        # Forecast
        future_data = forecast[forecast['ds'] > sales_data['ds'].max()]
        fig_forecast.add_trace(go.Scatter(
            x=future_data['ds'],
            y=future_data['yhat'],
            mode='lines',
            name='Forecast',
            line=dict(color='red', dash='dash')
        ))
        
        # Confidence intervals
        fig_forecast.add_trace(go.Scatter(
            x=future_data['ds'],
            y=future_data['yhat_upper'],
            mode='lines',
            line=dict(width=0),
            showlegend=False
        ))
        
        fig_forecast.add_trace(go.Scatter(
            x=future_data['ds'],
            y=future_data['yhat_lower'],
            mode='lines',
            line=dict(width=0),
            fill='tonexty',
            fillcolor='rgba(255, 0, 0, 0.1)',
            name='Confidence Interval'
        ))
        
        fig_forecast.update_layout(
            title=f"Sales Forecast - Next {forecast_days} Days",
            xaxis_title="Date",
            yaxis_title="Sales (₹)",
            height=500
        )
        
        st.plotly_chart(fig_forecast, use_container_width=True)
    
    # Forecast components
    if show_components:
        st.subheader("Forecast Components")
        
        components_fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=['Trend', 'Yearly Seasonality']
        )
        
        components_fig.add_trace(
            go.Scatter(x=forecast['ds'], y=forecast['trend'], name='Trend'),
            row=1, col=1
        )
        
        components_fig.add_trace(
            go.Scatter(x=forecast['ds'], y=forecast['yearly'], name='Yearly'),
            row=2, col=1
        )
        
        components_fig.update_layout(height=600)
        st.plotly_chart(components_fig, use_container_width=True)
    
    # Data insights with loading indicator
    st.markdown("---")
    st.subheader("💡 Business Insights")
    status_text.text("🧠 Analyzing business insights...")
    progress_bar.progress(95)
    
    with st.spinner("🧠 Analyzing business insights..."):
        col_insight1, col_insight2, col_insight3 = st.columns(3)
    
    with col_insight1:
        avg_discount = filtered_df['Discount'].mean()
        st.metric("Average Discount", f"{avg_discount:.1%}")
        if avg_discount > 0.2:
            st.error("⚠️ High average discount may be impacting profitability")
        else:
            st.success("✅ Discount levels appear reasonable")
    
    with col_insight2:
        negative_profit_pct = (filtered_df['Profit'] < 0).sum() / len(filtered_df) * 100
        st.metric("Orders with Negative Profit", f"{negative_profit_pct:.1f}%")
        if negative_profit_pct > 15:
            st.error("⚠️ High percentage of unprofitable orders")
        else:
            st.success("✅ Most orders are profitable")
    
    with col_insight3:
        best_category = filtered_df.groupby('Category')['Profit'].sum().idxmax()
        st.metric("Most Profitable Category", best_category)
        st.info(f"💡 Focus marketing efforts on {best_category}")
    
    # Raw data view
    with st.expander("View Raw Data"):
        st.dataframe(
            filtered_df.sort_values('Order Date', ascending=False),
            use_container_width=True
        )
        
        # Download button
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="Download filtered data as CSV",
            data=csv,
            file_name=f"retail_data_{date_range[0]}_{date_range[1]}.csv",
            mime="text/csv"
        )
    
    # Complete the analysis
    status_text.text("✅ Analysis complete!")
    progress_bar.progress(100)
    st.success("🎉 Dashboard analysis completed successfully!")

if __name__ == "__main__":
    main()

# Instructions to run:
"""
1. Install required packages:
   pip install streamlit pandas numpy plotly prophet openpyxl

2. Save this file as retail_dashboard.py

3. Run the dashboard:
   streamlit run retail_dashboard.py

4. Place your Global_Superstore.xls file in the same directory, 
   or the app will use sample data for demonstration.
"""