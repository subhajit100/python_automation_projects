# The below method extractCsv takes the fileName and newFileName, and we calculate the Data_value column sum upto 10 rows , and also store the value of three columns upto 10 rows into a new csv file. We also create a bar chart using matplotlib for the first 10 rows with x-axis = Period and y-axis = Data_value
import os
import csv
import matplotlib.pyplot as plt

# function for plotting the bar chart
def createBarChart(csvPath):
    try:
        periods = []
        data_values = []
        
        # Read the new CSV file
        with open(csvPath, mode='r') as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                try:
                    periods.append(row['Period'])
                    data_values.append(float(row['Data_value']))
                except ValueError:
                    print(f"Skipping invalid Data_value: {row['Data_value']}")
        
        # Plot the bar chart
        plt.figure(figsize=(10, 6))
        plt.bar(periods, data_values, color='skyblue')
        plt.xlabel("Period", fontsize=12)
        plt.ylabel("Data Value", fontsize=12)
        plt.title("Bar Chart of Data Values by Period", fontsize=14)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()
    except Exception as e:
        print(f"Error while drawing bar chart: {e}")    

# function for extracting the csv to a new csv with less columns and less rows
def extractCsv(fileName, newFileName):
    totalSum=0
    count=0
    selectedColumns = ['Period', 'Data_value', 'Series_title_2']
    sumColName = 'Data_value'

    try:
        currDir = os.path.dirname(__file__)
        filePath = os.path.join(currDir, fileName)
        newCsvPath = os.path.join(currDir, newFileName)
        with open(filePath, mode='r') as file:
            reader = csv.DictReader(file)
            for col in selectedColumns:
                if col not in reader.fieldnames:
                    raise ValueError(f"Column '{col}' not found in the CSV file.")

            # Open the new CSV file for writing
            with open(newCsvPath, mode='w', newline='') as outfile:
                writer = csv.DictWriter(outfile, fieldnames=selectedColumns)
                writer.writeheader()  # Write column headers
                
                # Iterate through rows and write only selected columns for first 10 rows
                for row in reader:
                    if count >= 10:  # Stop after 10 rows
                        break
                    try:
                        # Extract required columns and write to new file
                        writer.writerow({
                            selectedColumns[0] : row[selectedColumns[0]],
                            selectedColumns[1]: row[selectedColumns[1]],
                            selectedColumns[2] : row[selectedColumns[2]]
                        })
                        try:
                            totalSum += float(row[sumColName])
                            count+=1
                        except ValueError:
                            print(f"Skipping invalid value: {row[sumColName]}")
                    except KeyError:
                        print("Skipping row due to missing column data.")    
                
            if sumColName not in reader.fieldnames:
                    raise ValueError(f"{sumColName} column not found in the CSV file.")
                 
        createBarChart(newCsvPath)
        return totalSum
    except Exception as e:
         return f"Error: {e}"
    

fileName = 'business-data.csv'
newFileName = "extracted_data.csv"
totalSum=extractCsv(fileName, newFileName)    
print("total sum:", totalSum)