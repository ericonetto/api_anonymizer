import uvicorn

if __name__=="__main__":
    uvicorn.run("api_interface:app",host='0.0.0.0', port=4557, reload=True, workers=3)