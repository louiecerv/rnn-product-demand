import streamlit as st
import tensorflow as tf
import pandas as pd
import numpy as np
from sklearn.metrics import mean_squared_error, mean_absolute_error
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt
import time

def app():

    st.subheader('Store Item Demand Forecasting Using RNN-LSTM and GRU')

    text = """**Prof. Louie F. Cervantes, M. Eng. (Information Engineering)**
    \nCCS 229 - Intelligent Systems :: Department of Computer Science
    College of Information and Communications Technology
    **West Visayas State University**"""
    st.markdown(text)

    text = """This Streamlit app utilizes one of the following: a Recurrent Neural Network (RNN) with 
    Long Short-Term Memory (LSTM) units or a Gated Recurrent Units (GRU) to forecast future store item demand. 
    The model is trained on time series data provided by the Kaggle 'Store Item Demand 
    Forecasting Challenge' https://www.kaggle.com/competitions/demand-forecasting-kernels-only dataset. You can interact with the app to visualize 
    past sales data and generate predictions for future periods. Under the hood, the app 
    leverages Streamlit's capabilities to create a user-friendly interface for 
    exploring time series forecasting with LSTMs. """
    st.write(text) 

    text = """In this Kaggle challenge, participants tackle the task of forecasting monthly
    sales for specific items across multiple stores. The dataset consists of sales data 
    filtered by both store and item, encompassing 10 stores and 50 items in total. 
    To address this forecasting problem, a subset of the dataset is first created, 
    focusing on sales from a selected store and a chosen item.
    Utilizing a Recurrent Neural Network (RNN) architecture, specifically Long Short-Term 
    Memory (LSTM) model or a Gated Recurrent Units (GRU) the provided subset of sales data is used for training. 
    LSTM networks are adept at capturing temporal dependencies in sequential data, 
    making them suitable for time series forecasting tasks like this one.
    The LSTM model is trained on the subset of sales data to learn patterns and trends in 
    monthly sales over time. Once trained, the model is capable of generating predictions 
    for monthly sales for a specified number of years into the future. These predictions 
    provide valuable insights into future sales trends, aiding store managers and inventory 
    planners in making informed decisions.
    To visualize the predicted sales data, a time series plot is generated, illustrating the 
    forecasted monthly sales over the projected time period. This plot serves as a powerful 
    tool for understanding sales trends, identifying potential peaks or dips in demand, and 
    informing strategic decision-making processes.
    This solution leverages advanced deep learning techniques to forecast monthly sales 
    for specific items in individual stores, offering a data-driven approach to optimize 
    inventory management and enhance business performance in the retail sector."""
    with st.expander("Read About the Challenge and Solution"):
        st.write(text)  
    
    df = pd.read_csv('./data/train.csv')

    # Filter records based on store and item (assuming single values)
    options = df['store'].unique()
    # Create the option box using st.selectbox
    selected_option = st.sidebar.selectbox("Select a store:", options)
    store_to_filter = selected_option
    options = df['item'].unique()
    # Create the option box using st.selectbox
    selected_option = st.sidebar.selectbox("Select item:", options)
    item_to_filter = selected_option

    options = ['LSTM', 'GRU']
    # Create the option box using st.selectbox
    selected_option = st.sidebar.selectbox("Select model type:", options)
    model_type = selected_option

    st.sidebar.write("Lookback is the number of months for the model to consider when making predictions.")
    options = ['12', '24', '36', '48', '60']
    # Create the option box using st.selectbox
    selected_option = st.sidebar.selectbox("Set lookback:", options, index=2)
    look_back = int(selected_option)    

    filtered_df = df[(df['store'] == store_to_filter) & (df['item'] == item_to_filter)]

    df1 = filtered_df.copy()
    df1 = df1.loc[:, ['date', 'sales']]
    df1['date'] = pd.to_datetime(df1['date'])

    # Set the 'date' column as the index
    df1.set_index('date', inplace=True)

    # Resample to monthly data, summing sales for each month
    df1 = pd.DataFrame(df1.resample('ME')['sales'].sum())
    df1.index = pd.to_datetime(df1.index)

    with st.expander("Show Dataset"):
        st.write("The TIme Series Dataset")
        st.write(df1)   
        st.write(df1.shape)

    st.write("The Time Series Plot")

    fig, ax = plt.subplots()  
    ax.plot(df1['sales'])
    ax.set_title('Sales Over Time')
    ax.set_xlabel('Date')
    ax.set_ylabel('Sales')
    ax.grid(True)  
    # Limit the number of ticks on the x-axis to 10 (adjust as needed)
    plt.xticks(rotation=45)  # Rotate x-axis labels for better readability (optional)
    locator = plt.MaxNLocator(nbins=10)
    ax.xaxis.set_major_locator(locator)
    st.pyplot(fig)

    # Normalize the data
    scaler = MinMaxScaler(feature_range=(0, 1))
    data_norm = scaler.fit_transform(df1.iloc[:,0].values.reshape(-1, 1))
    data_norm = pd.DataFrame(data_norm)
    st.session_state.data_norm = data_norm

    # Split the data into training and testing sets
    train_size = int(len(data_norm) * 0.8)
    test_size = len(data_norm) - train_size
    train_data, test_data = data_norm.iloc[0:train_size], data_norm.iloc[train_size:len(data_norm)]

    # Convert the data to numpy arrays
    x_train, y_train = train_data.iloc[:-1], train_data.iloc[1:]
    x_test, y_test = test_data.iloc[:-1], test_data.iloc[1:]

    # Reshape the data to match the input shape of the LSTM model
    x_train = np.reshape(x_train.to_numpy(), (x_train.shape[0], 1, x_train.shape[1]))
    x_test = np.reshape(x_test.to_numpy(), (x_test.shape[0], 1, x_test.shape[1]))
    y_train = y_train.to_numpy()
    y_test = y_test.to_numpy()

    n_features = 1  # Number of features in your typhoon data

    if model_type == 'LSTM':
        model =  tf.keras.Sequential([  
            tf.keras.layers.Bidirectional(tf.keras.layers.LSTM(128, return_sequences=True), input_shape=(look_back, n_features)),
            tf.keras.layers.Dropout(0.3),
            tf.keras.layers.GRU(64, return_sequences=True),  # Another GRU layer
            tf.keras.layers.Dropout(0.2),
            tf.keras.layers.GRU(32),  # Reduced units for final layer
            tf.keras.layers.Dropout(0.1),
            tf.keras.layers.Dense(1)
        ])
    elif model_type == 'GRU':
        # Define the improved model architecture
        model = tf.keras.Sequential([
            tf.keras.layers.GRU(128, return_sequences=True, input_shape=(look_back, n_features)),
            tf.keras.layers.Dropout(0.3),
            
            # Add another GRU layer for better feature extraction
            tf.keras.layers.GRU(64, return_sequences=True),
            tf.keras.layers.Dropout(0.2),
            
            # Reduce the complexity of the model to prevent overfitting
            tf.keras.layers.GRU(32),
            tf.keras.layers.Dropout(0.1),
            
            # Introduce a dense layer with more neurons for better representation
            tf.keras.layers.Dense(64, activation='relu'),  # Add dense layer with ReLU activation
            tf.keras.layers.Dropout(0.1),
            
            # Add one more dense layer for better learning
            tf.keras.layers.Dense(32, activation='relu'),  # Add dense layer with ReLU activation
            tf.keras.layers.Dropout(0.1),
            
            # Output layer with one neuron for regression task
            tf.keras.layers.Dense(1)
        ])
            
    # Compile the model
    model.compile(loss="mse", optimizer="adam")  # You can adjust loss and optimizer based on your needs

    # Print model summary
    model.summary()

    if st.sidebar.button("Start Training"):
        if "model" not in st.session_state:
            st.session_state.model = model
        progress_bar = st.progress(0, text="Training the LSTM network, please wait...")           
        # Train the model
        history = model.fit(x_train, y_train, epochs=500, batch_size=64, validation_data=(x_test, y_test))

        fig, ax = plt.subplots()  # Create a figure and an axes
        ax.plot(history.history['loss'], label='Train')  # Plot training loss on ax
        ax.plot(history.history['val_loss'], label='Validation')  # Plot validation loss on ax

        ax.set_title('Model loss')  # Set title on ax
        ax.set_ylabel('Loss')  # Set y-label on ax
        ax.set_xlabel('Epoch')  # Set x-label on ax

        ax.legend()  # Add legend
        st.pyplot(fig)
        st.session_state.model = model

        # update the progress bar
        for i in range(100):
            # Update progress bar value
            progress_bar.progress(i + 1)
            # Simulate some time-consuming task (e.g., sleep)
            time.sleep(0.01)
        # Progress bar reaches 100% after the loop completes
        st.success("LSTM Network training completed!") 

    years = st.sidebar.slider(   
        label="Number years to forecast:",
        min_value=1,
        max_value=6,
        value=4,
        step=1
    )

    if st.sidebar.button("Predictions"):
        if "model" not in st.session_state:
            st.error("Please train the model before making predictions.")  
            return
        
        # Get the predicted values and compute the accuracy metrics
        y_pred_train = model.predict(x_train)
        y_pred_test = model.predict(x_test)

        train_rmse = np.sqrt(mean_squared_error(y_train, y_pred_train))
        test_rmse = np.sqrt(mean_squared_error(y_test, y_pred_test))
        train_mae = mean_absolute_error(y_train, y_pred_train)
        test_mae = mean_absolute_error(y_test, y_pred_test)
        st.write('Train RMSE:', train_rmse)
        st.write('Test RMSE:', test_rmse)
        st.write('Train MAE:', train_mae)
        st.write('Test MAE:', test_mae)

        model = st.session_state.model
        data_norm = st.session_state.data_norm
        # Get predicted data from the model using the normalized values
        predictions = model.predict(data_norm)

        # Inverse transform the predictions to get the original scale
        predvalues = scaler.inverse_transform(np.array(predictions).reshape(-1, 1))
  
        # Convert predvalues to integers
        predvalues_int = predvalues.astype(int)

        # Create a DataFrame with a column named "sales"
        predvalues = pd.DataFrame({'sales': predvalues_int.flatten()})

        # use the same index as the original data
        predvalues.index = df1.index

        pred_period = years * 12    
        # Use the model to predict the next year of data
        input_seq_len = look_back         

        # check that look_back is less than the length of the data
        last_seq = data_norm[-input_seq_len:] 

        preds = []
        for i in range(pred_period):
            pred = model.predict(last_seq)
            preds.append(pred[0])

            last_seq = np.array(last_seq)
            last_seq = np.vstack((last_seq[1:], pred[0]))
            last_seq = pd.DataFrame(last_seq)

        # Inverse transform the predictions to get the original scale
        prednext = scaler.inverse_transform(np.array(preds).reshape(-1, 1))

        #flatten the array from 2-dim to 1-dim
        prednext = [item for sublist in prednext for item in sublist]

        # Convert prednext to integers
        prednext = [int(x) for x in prednext]

        end_dates = {
            12: '2018-12',
            24: '2019-12',
            36: '2020-12',
            48: '2021-12',
            60: '2022-12',
            72: '2023-12'
        }

        end = end_dates.get(pred_period, None)

        months = pd.date_range(start='2018-01', end=end, freq='MS')

        # Create a DataFrame with a column named "sales"
        nextyear = pd.DataFrame(prednext, index=months, columns=["sales"])

        # Concatenate along the rows (axis=0)
        combined_df = pd.concat([df1, nextyear], axis=0)

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.set_title('Comparison of Actual and Predicted Sales')

        ax.plot(predvalues['sales'], color='red', linestyle='--', label='Model Predictions')  # dotted line for model predictions

        # Plot df1's sales values with one linestyle
        ax.plot(df1['sales'], color = 'blue', linestyle='-', label='Original Data')

        # Plot projected sales values with a different linestyle
        ax.plot(combined_df.index[len(df1):], combined_df['sales'][len(df1):], color = 'red', marker = 'o', linestyle='-', label='Projected Sales')

        max_y_value = max(df1['sales'].values.max(), nextyear['sales'].max()) + 2
        ax.set_ylim(0, max_y_value)

        ax.set_xlabel('\nMonth', fontsize=20, fontweight='bold')
        ax.set_ylabel('Sales', fontsize=20, fontweight='bold')

        ax.set_xlabel('Month')
        ax.set_ylabel('Sales')
        ax.grid(True)
        ax.tick_params(axis='x', rotation=45)
        # Add the legend
        ax.legend()  # This line adds the legend
        fig.tight_layout()
        st.pyplot(fig)

        st.write('Predicted Sales for the next', years, 'years:')

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(nextyear['sales'], marker='o', linestyle='-')
        ax.set_title('Projected Sales Over Time')
        ax.set_xlabel('Month')
        ax.set_ylabel('Sales')
        ax.grid(True)
        ax.tick_params(axis='x', rotation=45)
        fig.tight_layout()
        st.pyplot(fig)

        with st.expander("Show Predicted Sales Table"):
            st.write("The Predicted Dataset")
            st.write(nextyear)   
            st.write(nextyear.shape)

        with st.expander("Read About the Lookback"):
            text = """When discussing the performance of an RNN LSTM (Recurrent Neural 
            Network Long Short-Term Memory) model on item sales forecast data, it's 
            crucial to consider the impact of the "lookback" period on the model's 
            predictive capability. The "lookback" period refers to the number of 
            previous time steps the model uses to make predictions. In your scenario, 
            the lookback period is varied between 12 months and 36 months.
            \nWhen the lookback is set to a small number, such as 12 months, 
            the model is better at capturing short-term patterns and fluctuations 
            in sales data. This is because it focuses on recent history, enabling it 
            to adapt quickly to changes in consumer behavior, seasonal trends, or 
            promotional activities. As a result, the model may exhibit strong 
            performance in predicting the changing patterns of sales over shorter 
            time horizons.
            \nHowever, as the lookback period increases to 36 months or longer, 
            the model's ability to capture short-term fluctuations diminishes. 
            Instead, it starts to emphasize longer-term trends and patterns in the data. 
            While this may lead to more stable and consistent predictions over longer 
            time horizons, it may also result in a loss of sensitivity to short-term dynamics. 
            Consequently, the model may predict lower sales overall, as it focuses more on 
            the average behavior observed over the extended period.
            \nIn essence, the choice of lookback period involves a trade-off 
            between capturing short-term fluctuations and maintaining a broader 
            perspective on long-term trends. A shorter lookback period enables the 
            model to react quickly to changes but may sacrifice accuracy over 
            longer periods. Conversely, a longer lookback period provides a more 
            stable outlook but may overlook short-term dynamics."""
            st.write(text)

if __name__ == "__main__":
    app()   
