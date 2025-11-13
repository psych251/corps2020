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

# Define Expected Answer Dictory
ExpAns_dic = {'1P': 'A knife and fork',
              '2P': 'Andy Murray',
              '3P': 'Big Ben',
              '4P': 'Black and white',
              '5P': 'Buckingham Palace',
              '6P': 'Buzz Lightyear',
              '7P': 'December twenty fifth',
              '8P': 'Donald Trump',
              '9P': 'Ham and Pineapple',
              '10P': 'Harry Potter',
              '11P': 'Hillary Clinton',
              '12P': 'It hit an iceberg',
              '13P': 'James Bond',
              '14P': 'Kings Cross',
              '15P': 'Molly and Arthur',
              '16P': 'New Years Eve',
              '17P': 'New York',
              '18P': 'October thirty first',
              '19P': 'Snow White',
              '20P': 'Ten Downing Street',
              '21P': 'The Amazon river',
              '22P': 'The Eiffel Tower',
              '23P': 'The Northe Pole',
              '24P': 'The Northern Lights',
              '25P': 'The Thames',
              '26P': 'The Tube',
              '27P': 'The White House',
              '28P': 'Theresa May',
              '30P': 'Twice a day',
              '31P': 'Robin Hood',
              '1U': 'A knife and fork',
              '2U': 'Andy Murray',
              '3U': 'Big Ben',
              '4U': 'Black and white',
              '5U': 'Buckingham Palace',
              '6U': 'Buzz Lightyear',
              '7U': 'December twenty fifth',
              '8U': 'Donald Trump',
              '9U': 'Ham and Pineapple',
              '10U': 'Harry Potter',
              '11U': 'Hillary Clinton',
              '12U': 'It hit an iceberg',
              '13U': 'James Bond',
              '14U': 'Kings Cross',
              '15U': 'Molly and Arthur',
              '16U': 'New Years Eve',
              '17U': 'New York',
              '18U': 'October thirty first',
              '19U': 'Snow White',
              '20U': 'Ten Downing Street',
              '21U': 'The Amazon river',
              '22U': 'The Eiffel Tower',
              '23U': 'The Northe Pole',
              '24U': 'The Northern Lights',
              '25U': 'The Thames',
              '26U': 'The Tube',
              '27U': 'The White House',
              '28U': 'Theresa May',
              '30U': 'Twice a day',
              '31U': 'Robin Hood',}

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
        return match.group(1)
    return ''

def extract_trial_from_node_id(node_id):
    """Extract the trial-relevant number from internal_node_id to handle multiple responses of demographic questions"""
    if pd.isna(node_id):
        return None
    # get the second part of internal_node_id (00-7.0)
    try:
        parts = str(node_id).split('-')
        if len(parts) >1 :
            last_part = parts[-1]
            number = int(last_part.split('.')[0])
            return number
    except (ValueError, IndexError):
        return None
    return None

def parse_list_file(filepath, stimulus_data):
    """Parse a single List_*.csv file"""
    df = pd.read_csv(filepath)
    
    # Extract metadata from filename
    filename = os.path.basename(filepath)
    # Updated regex to match any two letter combination after List_*_
    list_match = re.search(r'List_(\w+)_[A-Z]{2}', filename)
    list_name = list_match.group(1) if list_match else ''
    
    # Filter for survey-text rows (these contain participant responses)
    survey_rows = df[df['trial_type'] == 'survey-text'].copy()
    
    # Get participant ID and trial order from first row
    if len(df) > 0:
        participant_id = df['subject'].iloc[0]
    else:
        return pd.DataFrame()
    
    results = []
    
    # Process each survey response
    for idx, row in survey_rows.iterrows():
        try:
            responses_dict = json.loads(row['responses'])
            
            # Skip demographic survey (has Q1, Q2, Q3, Q4)
            # Only process responses that have ONLY Q0 (the actual question responses)
            if 'Q1' not in responses_dict and 'Q0' in responses_dict:
                response_text = responses_dict['Q0']

                # extrac trial number from internal_node_id
                trial_num = extract_trial_from_node_id(row.get('internal_node_id'))
                
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
                            'Trial': trial_num,
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
                            'Expected Answer': ExpAns_dic.get(qfile, ''), 
                            'EA Wlength': count_words(ExpAns_dic.get(qfile, '')),
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
        except (json.JSONDecodeError, KeyError) as e:
            print(f"  Warning: Could not parse row {idx}: {e}")
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

        # Ad-hoc amendation for naming error in the original stimulus
        # Fixed version: use .replace() or .loc instead of if statement
        combined_df['Heard Answer'] = combined_df['Heard Answer'].replace('North Pole', 'The North Pole')
        
        # sanity check
        print(f"  Trial range after mutation: {combined_df['Trial'].min():.0f} - {combined_df['Trial'].max():.0f}")
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