import pandas as pd

def main():
    
    # Load the dataset
    df = pd.read_csv("data/customer_churn_business_dataset.csv", delimiter=",")
    
    # Check for missing values
    print(df.isnull().sum())

    # Display the data types of each column
    print(df.dtypes) 

    # Interesting columns to expore
    print(df["churn"].value_counts())   # Target variable (0 = No, 1 = Yes)   

if __name__ == "__main__":
    main()