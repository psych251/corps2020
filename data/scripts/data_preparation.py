import pandas as pd
import json
import glob
import os
import re

# Define the target columns from dprime.csv
TARGET_COLUMNS = [
    'ItemNo', 'Participant', 'Trial', 'ACondition', 'Plaus', 'Heard Answer', 
    'HA Wlength', 'Anumber', 'List', 'QCondition', 'QFile', 'Qnumber', 
    'Question', 'Expected Answer', 'EA Wlength', 'QLSA', 'response', 
    'Correct', 'Incorrect', 'Prop Heard', 'Block', 'Plaus HIT', 
    'Plaus Incorrect', 'NumberOfPlausibleWordsReported', 
    'NumberOfPlausibleWordsNotReported', 'Prop Expected'
]

def load_stimulus_lists(stimulus_file):
    """Load all stimulus list sheets from Excel file into a lookup dictionary"""
    stimulus_data = {}
    
    # Read all sheets
    xlsx = pd.ExcelFile(stimulus_file)
    for sheet_name in xlsx.sheet_names:
        df = pd.read_excel(stimulus_file, sheet_name=sheet_name)
        # Create key from sheet name (e.g., "List 1a" -> "1a")
        list_key = sheet_name.replace('List ', '').strip()
        stimulus_data[list_key] = df
    
    return stimulus_data

def get_stimulus_info(stimulus_data, list_name, qfile):
    """Get stimulus information for a given list and QFile"""
    if list_name not in stimulus_data:
        return None
    
    df = stimulus_data[list_name]
    
    # Extract QFile number (e.g., "9P" from "9P.wav" or "9P.mp3")
    qfile_clean = qfile.replace('.wav', '').replace('.mp3', '')
    
    # Find matching row by QFile
    # QFile column might have .wav extension
    matching_rows = df[df['QFile'].str.contains(qfile_clean, na=False, regex=False)]
    
    if len(matching_rows) > 0:
        return matching_rows.iloc[0].to_dict()
    
    return None

def count_words(text):
    """Count number of words in a text string"""
    if pd.isna(text) or text == '':
        return 0
    return len(str(text).strip().split())

def extract_qfile_from_stimulus(stimulus):
    """Extract QFile number from stimulus path"""
    if pd.isna(stimulus):
        return ''
    match = re.search(r'questions/(\d+[PU])\.mp3', str(stimulus))
    if match:
        return match.group(1)
    return ''

def extract_heard_answer(stimulus):
    """Extract heard answer from stimulus path"""
    if pd.isna(stimulus):
        return ''
    match = re.search(r'answers/(.+?)\.mp3', str(stimulus))
    if match:
        return match.group(1).replace('.mp3', '')
    return ''

def parse_list_file(filepath, stimulus_data):
    """Parse a single List_*.csv file"""
    df = pd.read_csv(filepath)
    
    # Extract metadata from filename
    filename = os.path.basename(filepath)
    list_match = re.search(r'List_(\w+)_PP', filename)
    list_name = list_match.group(1) if list_match else ''
    
    # Filter for survey-text rows (these contain participant responses)
    survey_rows = df[df['trial_type'] == 'survey-text'].copy()
    
    # Get participant ID and trial order from first row
    if len(df) > 0:
        participant_id = df['subject'].iloc[0]
        trial_order_str = df['trial'].iloc[0]
    else:
        return pd.DataFrame()
    
    results = []
    
    # Process each survey response
    for idx, row in survey_rows.iterrows():
        # Skip the demographic survey (first survey-text entry)
        try:
            responses_dict = json.loads(row['responses'])
            if 'Q0' in responses_dict and responses_dict.get('Q1') is None:
                # This is likely a question response
                response_text = responses_dict['Q0']
                
                # Find the corresponding question audio (should be a few rows before)
                question_audio_row = df[(df.index < idx) & 
                                       (df['trial_type'] == 'single-audio') & 
                                       (df['stimulus'].str.contains('questions', na=False))].tail(1)
                
                # Find the corresponding answer audio
                answer_audio_row = df[(df.index < idx) & 
                                     (df['trial_type'] == 'single-audio') & 
                                     (df['stimulus'].str.contains('answers', na=False))].tail(1)
                
                if not question_audio_row.empty and not answer_audio_row.empty:
                    qfile = extract_qfile_from_stimulus(question_audio_row.iloc[0]['stimulus'])
                    heard_answer = extract_heard_answer(answer_audio_row.iloc[0]['stimulus'])
                    
                    # Get stimulus info from lookup table
                    stim_info = get_stimulus_info(stimulus_data, list_name, qfile)
                    
                    if stim_info:
                        # Determine condition based on QFile
                        if 'P' in qfile:
                            qcondition = 'Predictable'
                        elif 'U' in qfile:
                            qcondition = 'Unpredictable'
                        else:
                            qcondition = ''
                        
                        # Create result row with data from stimulus list
                        result = {
                            'ItemNo': stim_info.get('ItemNo', ''),
                            'Participant': participant_id,
                            'Trial': row['trial_index'],
                            'ACondition': stim_info.get('ACondition', ''),
                            'Plaus': stim_info.get('Aplaus', ''),
                            'Heard Answer': heard_answer,
                            'HA Wlength': stim_info.get('Wlength', count_words(heard_answer)),
                            'Anumber': stim_info.get('Anumber', ''),
                            'List': list_name,
                            'QCondition': stim_info.get('QCondition', qcondition),
                            'QFile': qfile,
                            'Qnumber': stim_info.get('Qnumber', ''),
                            'Question': stim_info.get('Question', ''),
                            'Expected Answer': stim_info.get('Answer', ''),
                            'EA Wlength': count_words(stim_info.get('Answer', '')),
                            'QLSA': stim_info.get('QLSA', ''),
                            'response': response_text,
                            'Correct': '',  # To be calculated
                            'Incorrect': '',  # To be calculated
                            'Prop Heard': '',  # To be calculated
                            'Block': '',  # To be determined based on trial position
                            'Plaus HIT': '',
                            'Plaus Incorrect': '',
                            'NumberOfPlausibleWordsReported': '',
                            'NumberOfPlausibleWordsNotReported': '',
                            'Prop Expected': ''
                        }
                        
                        results.append(result)
        except (json.JSONDecodeError, KeyError):
            continue
    
    return pd.DataFrame(results)

def main():
    # Load stimulus lists
    stimulus_file = '/Users/xirohu/ResearchProj/corps2020/Experiment/Stimulus_List.xlsx'
    print("Loading stimulus lists from Excel file...")
    stimulus_data = load_stimulus_lists(stimulus_file)
    print(f"Loaded {len(stimulus_data)} stimulus lists: {list(stimulus_data.keys())}")
    
    # Find all List CSV files
    input_dir = '/Users/xirohu/ResearchProj/corps2020/data/raw/pilotA'
    list_files = glob.glob(os.path.join(input_dir, 'List_*.csv'))
    
    print(f"\nFound {len(list_files)} List files:")
    for f in list_files:
        print(f"  - {os.path.basename(f)}")
    
    # Process all files
    all_data = []
    for filepath in list_files:
        print(f"\nProcessing {os.path.basename(filepath)}...")
        df = parse_list_file(filepath, stimulus_data)
        if not df.empty:
            print(f"  Extracted {len(df)} responses")
            all_data.append(df)
        else:
            print(f"  No data extracted")
    
    # Combine all data
    if all_data:
        combined_df = pd.concat(all_data, ignore_index=True)

        # Mutate trial number and assign block value
        combined_df = combined_df[(combined_df['Trial'] - 2) % 5 == 0].copy()
        print("\nApplying trial mutation and block assignment...")
        combined_df['Trial'] = (combined_df['Trial'] - 2) // 5
        
        # Assign Block based on Trial value
        combined_df['Block'] = combined_df['Trial'].apply(
            lambda x: 1 if x <= 5 else (2 if x <= 10 else 3)
        )
        
        # sanity check
        print(f"  Trial range after mutation: {combined_df['Trial'].min():.2f} - {combined_df['Trial'].max():.2f}")
        print(f"  Block distribution:")
        print(f"    Block 1: {(combined_df['Block'] == 1).sum()} rows")
        print(f"    Block 2: {(combined_df['Block'] == 2).sum()} rows")
        print(f"    Block 3: {(combined_df['Block'] == 3).sum()} rows")
        
        # Ensure all target columns are present
        for col in TARGET_COLUMNS:
            if col not in combined_df.columns:
                combined_df[col] = ''
        
        # Reorder columns to match dprime.csv
        combined_df = combined_df[TARGET_COLUMNS]

        # mutate

        
        # Save to output
        output_path = '/Users/xirohu/ResearchProj/corps2020/data/processed/transformed_dprime.csv'
        combined_df.to_csv(output_path, index=False)
        print(f"\n✓ Successfully created {output_path}")
        print(f"  Total rows: {len(combined_df)}")
        print(f"  Columns: {len(combined_df.columns)}")
        
        # Show sample of data
        print("\nSample of transformed data:")
        print(combined_df[['Participant', 'ItemNo', 'ACondition', 'Plaus', 'QFile', 'Question', 'response']].head(10).to_string())
    else:
        print("\nNo data to process!")

if __name__ == '__main__':
    main()