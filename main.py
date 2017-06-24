from os import listdir
import pygame
import mido
import numpy as np
import random
import time
INPUT_DIRECTORY = 'bach/'
VELOCITY = 32
TIME = 150
# return the next node given a note
def get_next_note(first_note, weight_matrix):
    next_note_prob = weight_matrix[first_note]
    all_zeros = not np.any(next_note_prob)
    if all_zeros:
        rand_note = random.uniform(0,127)
        print('random note:', rand_note)
        return rand_note


    next_note = np.random.choice(128, p=next_note_prob)
    # print('selected note:', next_note)
    return next_note

def train_file(filepath, weight_matrix):
    mid = mido.MidiFile(filepath)
    for i, track in enumerate(mid.tracks):
        note_ons = [msg.note for msg in track if msg.type == 'note_on']
        for i in range(len(note_ons) - 1):
            a = note_ons[i]
            b = note_ons[i+1]
            weight_matrix[a][b] += 1

def main():
    filepaths = listdir(INPUT_DIRECTORY)
    weight_matrix = np.zeros((128, 128), dtype=np.float64)
    for filepath in filepaths:
        train_file(INPUT_DIRECTORY + filepath, weight_matrix)
        print('done training file', filepath)
        print(np.count_nonzero(weight_matrix))
    # let's convert weight_matrix into probabilities
    # maybe use softmax, for now do standard normalization
    for i in range(len(weight_matrix)):
        second_note_array = weight_matrix[i]
        total = np.sum(second_note_array)
        if total == 0:
            continue
        else:
            weight_matrix[i] = second_note_array / total

    non_zero = np.transpose(np.nonzero(weight_matrix))

    # get a starting note
    starting_note = non_zero[0][0]
    # play 100 notes and save it into a file
    generated_notes = []
    for i in range(200):
        next_note = get_next_note(starting_note, weight_matrix)
        generated_notes.append(next_note)
        starting_note = next_note

    mid = mido.MidiFile()
    track = mido.MidiTrack()
    mid.tracks.append(track)
    for note in generated_notes:
        track.append(mido.Message('note_on', note=note, velocity=VELOCITY, time=TIME))
        track.append(mido.Message('note_off', note=note, velocity=127, time=TIME))
    OUTPUT = 'output/' + time.strftime('%H:%M:%S') + '.mid'
    mid.save(OUTPUT)

    pygame.init()
    pygame.mixer.music.load(OUTPUT)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.wait(1000)

main()