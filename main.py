# Imports
import os
import time
start_time = time.time()

i = 0
count = 0
state = 0
lines = []
failure = 0
success = 0
prediction = 0
instruction = ""
branch_target = 0
taken_counter = 0
program_counter = 0
predictor_penalty = 0
not_taken_counter = 0
next_program_counter = 0

history_table = [["", "", ""], ["", "", ""], ["", "", ""], ["", "", ""]
                 , ["", "", ""], ["", "", ""], ["", "", ""], ["", "", ""]
                 , ["", "", ""], ["", "", ""], ["", "", ""], ["", "", ""]
                 , ["", "", ""], ["", "", ""], ["", "", ""], ["", "", ""]
                 , ["", "", ""], ["", "", ""], ["", "", ""], ["", "", ""]
                 , ["", "", ""], ["", "", ""], ["", "", ""], ["", "", ""]
                 , ["", "", ""], ["", "", ""], ["", "", ""], ["", "", ""]
                 , ["", "", ""], ["", "", ""], ["", "", ""], ["", "", ""]
                 , ["", "", ""], ["", "", ""], ["", "", ""], ["", "", ""]
                 , ["", "", ""], ["", "", ""], ["", "", ""], ["", "", ""]
                 , ["", "", ""], ["", "", ""], ["", "", ""], ["", "", ""]
                 , ["", "", ""], ["", "", ""], ["", "", ""], ["", "", ""]
                 , ["", "", ""], ["", "", ""], ["", "", ""], ["", "", ""]
                 , ["", "", ""], ["", "", ""], ["", "", ""], ["", "", ""]
                 , ["", "", ""], ["", "", ""], ["", "", ""], ["", "", ""]
                 , ["", "", ""], ["", "", ""], ["", "", ""], ["", "", ""]
                 , ["", "", ""], ["", "", ""], ["", "", ""], ["", "", ""]
                 , ["", "", ""], ["", "", ""], ["", "", ""], ["", "", ""]
                 , ["", "", ""], ["", "", ""], ["", "", ""], ["", "", ""]
                 , ["", "", ""], ["", "", ""], ["", "", ""], ["", "", ""]
                 , ["", "", ""], ["", "", ""], ["", "", ""], ["", "", ""]
                 , ["", "", ""], ["", "", ""], ["", "", ""], ["", "", ""]
                 , ["", "", ""], ["", "", ""], ["", "", ""], ["", "", ""]
                 , ["", "", ""], ["", "", ""], ["", "", ""], ["", "", ""]
                 , ["", "", ""], ["", "", ""], ["", "", ""], ["", "", ""]
                 , ["", "", ""], ["", "", ""], ["", "", ""], ["", "", ""]
                 , ["", "", ""], ["", "", ""], ["", "", ""], ["", "", ""]
                 , ["", "", ""], ["", "", ""], ["", "", ""], ["", "", ""]
                 , ["", "", ""], ["", "", ""], ["", "", ""], ["", "", ""]
                 , ["", "", ""], ["", "", ""], ["", "", ""], ["", "", ""]
                 , ["", "", ""], ["", "", ""], ["", "", ""], ["", "", ""]
                 , ["", "", ""], ["", "", ""], ["", "", ""], ["", "", ""]]


branch_instructions = ["beq", "bne", "bge", "blt", "ble", "bgt"]

# , "bgeu", "bltu", "bgtu", "bleu"

location = r'C:\users\achyu\Desktop'


def read_log():

    for filename in os.listdir(location):
        global lines
        if filename == 'coremark_b.log':
            f = open(os.path.join(location, 'coremark_b.log'), "r")
            lines = f.readlines()
            f.close()


def branch_state_checker(a_list):
    global count, taken_counter, not_taken_counter, branch_target, next_program_counter, program_counter, instruction, state, success, failure
    for line in a_list:
        count += 1
        if count >= 1:
            columns = line.split('|')
            instruction = columns[-1]
            branch_instruction_string = instruction.split('-')
            program_counter = int(columns[4], 16)
            branch_instruction_container = branch_instruction_string[1].split()
            branch_instruction = branch_instruction_container[0]
            for ins in branch_instructions:
                if branch_instruction.find(ins) != -1:
                    branch_target_container = branch_instruction_container[1].split(',')
                    # backwards_predictor(program_counter, branch_target)
                    if len(branch_target_container) < 3:
                        branch_target = branch_target_container[1]
                        branch_target = int(branch_target, 16)
                    else:
                        branch_target = branch_target_container[2]
                        branch_target = int(branch_target, 16)
                    next_program_counter_container = a_list[count].split('|')
                    next_program_counter = next_program_counter_container[4]
                    # print(branch_target_container, instruction, next_program_counter)
                    if int(next_program_counter, 16) == branch_target:
                        taken_counter += 1
                        state = 1
                    else:
                        not_taken_counter += 1
                        state = 0
                    hybrid_predictor(program_counter, branch_target, state, 128)

    print("success:" + str(success))
    print("failure:" + str(failure))
    print("penalty for missed cycles: " + str(failure * 2))
    print("Really taken:" + str(taken_counter))
    print("Cycles wasted by predicting all not taken: " + str(taken_counter * 2))
    print("Really not taken:" + str(not_taken_counter))
    print( "Total branches" + " " +str(taken_counter + not_taken_counter))
    print("Success(%):" + str((success/(success+failure))*100))
    print("Run-time: " + str(time.time() - start_time))


def backwards_predictor(pc, bt):
    global success, failure, predictor_penalty, prediction
    if bt < pc:
        prediction = 1
        if prediction == state:
            success += 1
        else:
            failure += 1
    else:
        prediction = 0
        if prediction == state:
            success += 1
        else:
            failure += 1
    predictor_penalty = 2*failure


def history_predictor(pc, bt, status, table_size):
    global  program_counter, branch_target, success, failure, i
    i = ((i) % (table_size))
    absence_counter = 0

    for index in range(table_size):
        if history_table[index][1] == program_counter:
            prediction = history_table[index][0]
            if prediction == status:
                success += 1
                history_table[i][0] = status
                break
            else:
                failure += 1
                history_table[index][0] = status
                break
        else:
            absence_counter += 1
            if absence_counter == table_size:
                failure += 1
                break

    history_table[i][0] = status
    history_table[i][1] = pc
    history_table[i][2] = bt
    i += 1


def hybrid_predictor(pc, bt, status, table_size):
    global  program_counter, branch_target, success, failure, i, prediction
    i = ((i) % (table_size))
    absence_counter = 0

    for index in range(table_size):
        if history_table[index][1] == program_counter:
            prediction = history_table[index][0]
            if prediction == status:
                success += 1
                history_table[i][0] = status
                break
            else:
                failure += 1
                history_table[index][0] = status
                break
        else:
            absence_counter += 1
            if absence_counter == table_size:
                backwards_predictor(pc, bt)
                break

    history_table[i][0] = status
    history_table[i][1] = pc
    history_table[i][2] = bt
    i += 1


read_log()
branch_state_checker(lines)
