# Retail Analytics Dashboard - Deployment Guide

## Local Deployment

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Installation Steps

1. **Install Dependencies**
```bash
pip install -r requirements.txt
```

2. **Run the Dashboard**
```bash
streamlit run sales.py
```

3. **Access Dashboard**
- Open browser to: http://localhost:8501

## Streamlit Cloud Deployment

### Method 1: Direct Upload

1. **Prepare Files**
   - Ensure `sales.py` is in your project root
   - Include `requirements.txt`
   - Include `.streamlit/config.toml`

2. **Upload to GitHub**
   - Create a GitHub repository
   - Upload all files
   - Make sure `sales.py` is in the root directory

3. **Deploy on Streamlit Cloud**
   - Go to https://share.streamlit.io
   - Connect your GitHub repository
   - Select the main branch
   - Set the main file path to `sales.py`
   - Click "Deploy"

### Method 2: Using Streamlit CLI

1. **Install Streamlit CLI**
```bash
pip install streamlit
```

2. **Login to Streamlit Cloud**
```bash
streamlit login
```

3. **Deploy from Local**
```bash
streamlit deploy
```

## Troubleshooting

### Common Issues

#### 1. ModuleNotFoundError
**Problem**: Missing dependencies
**Solution**: 
```bash
pip install -r requirements.txt
```

#### 2. NumPy Compatibility Error
**Problem**: NumPy version conflicts
**Solution**:
```bash
pip install "numpy<2" --force-reinstall
```

#### 3. Prophet Installation Issues
**Problem**: Prophet fails to install
**Solution**:
```bash
pip install prophet --no-cache-dir
```

#### 4. Streamlit Cloud Deployment Fails
**Problem**: Dependencies not found
**Solution**: 
- Check `requirements.txt` includes all packages
- Ensure version constraints are correct
- Try deploying with minimal requirements first

### Requirements.txt Contents
```
streamlit>=1.28.0
pandas>=1.5.0
numpy>=1.21.0,<2.0.0
plotly>=5.0.0
prophet>=1.1.0
openpyxl>=3.0.0
bottleneck>=1.3.0
```

## Performance Optimization

### For Large Datasets
- Use data sampling for files > 10MB
- Implement caching with `@st.cache_data`
- Consider pagination for very large datasets

### For Streamlit Cloud
- Keep file sizes under 200MB
- Use efficient data processing
- Implement proper error handling

## Security Considerations

- No sensitive data in code
- Use environment variables for secrets
- Implement proper data validation
- Clear sensitive data after processing

## Monitoring and Maintenance

### Health Checks
- Test all imports on startup
- Validate data structure
- Monitor memory usage
- Check error logs

### Updates
- Keep dependencies updated
- Test with new data formats
- Monitor performance metrics
- Update documentation

## Support

### Local Issues
- Check Python version compatibility
- Verify all packages installed
- Test imports individually
- Check file permissions

### Cloud Issues
- Verify GitHub repository structure
- Check requirements.txt format
- Monitor deployment logs
- Test with minimal example first

---

**Last Updated**: October 2024  
**Version**: 2.0  
**Compatibility**: Python 3.8+, Streamlit 1.28+
