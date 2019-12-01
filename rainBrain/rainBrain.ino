#include <Adafruit_BMP085.h>
#include <math.h>
#include <EEPROM.h>
#include "dataset.h"
#define LED_PIN_WHITE 4
#define LED_PIN_BLUE 6
#define K_NEIGHBORS 9
#define MILLISECONDS_30MIN 1800000
#define WHITE_PWN 90


Adafruit_BMP085 bmp;
short altitude = 0;

float euclidean_distance_2d(float x0, float x1, float y0, float y1)
{
  return sqrt(pow(x1 - x0, 2) + pow(y1 - y0, 2));
}

float calc_presure_delta(float pressure, float previous_pressure)
{
  return (pressure - previous_pressure) / 2;
}

byte get_tag(byte *tags)
{
  int sum = 0;
  for (byte i = 0; i < K_NEIGHBORS; i++) {
    sum  += tags[i];
  }
  return sum > floor(K_NEIGHBORS / 2) ? 1 : 0;
}


void sort_arrays(float *distance_arr, byte *tag_arr)
{
  byte min_idx = 0;
  for (byte i = 0; i < K_NEIGHBORS-1; ++i) {
    min_idx = i;
    for (byte j = i+1; j < K_NEIGHBORS; ++j) {
      if (distance_arr[j] < distance_arr[min_idx]) {
        min_idx = j;
      }
    }
    float temp_dist;
    bool temp_tag;
    temp_dist = distance_arr[min_idx];
    distance_arr[min_idx] = distance_arr[i];
    distance_arr[i] = temp_dist;

    temp_tag = tag_arr[min_idx];
    tag_arr[min_idx] = tag_arr[i];
    tag_arr[i] = temp_tag;
  }
}

byte run_knn(float pressure, float delta)
{
  float neighbors_distance[K_NEIGHBORS] = {};
  byte neighbors_tag[K_NEIGHBORS] = {};

  //fill arrays with some data
  for (byte i = 0; i < K_NEIGHBORS; ++i) {
    neighbors_distance[i] = euclidean_distance_2d(pressure, dataset[i][0], delta, dataset[i][1]);
    neighbors_tag[i] = data_tag[i];
  }
  sort_arrays(neighbors_distance, neighbors_tag);

  // calculate the rest of the distances and find K smallest distances
  for (int i = K_NEIGHBORS; i < SIZE_DATASET; ++i) {
    float dist =  euclidean_distance_2d(pressure, dataset[i][0], delta, dataset[i][1]);
    for (byte j = 0; j < K_NEIGHBORS; j--) {
      if (dist <= neighbors_distance[j]) {
        neighbors_distance[K_NEIGHBORS-1] = dist;
        neighbors_tag[K_NEIGHBORS-1] = data_tag[i];
        break;
      }
    }
    sort_arrays(neighbors_distance, neighbors_tag);
  }
  return get_tag(neighbors_tag);
}

void setup() {
  pinMode(LED_PIN_BLUE, OUTPUT);
  digitalWrite(LED_PIN_BLUE, LOW);
  pinMode(LED_PIN_WHITE, OUTPUT);
  analogWrite(LED_PIN_WHITE, 255 - WHITE_PWN);
  EEPROM.get(0, altitude);   
  Serial.begin(9600);
  delay(1000);

  Serial.print("Current altitude set to:");
  Serial.println(altitude);
  Serial.print("Set new altitude: ");

  int timeout = 1000;
  while (Serial.available() == 0) {
     delay(10);
     if(--timeout == 0) {
      break;
     }
  }
  if(timeout > 0) {
    altitude = Serial.parseFloat();
    EEPROM.put(0, altitude); 
    Serial.println("\nNew altitude saved");
  }
  
  if (!bmp.begin()) {
    Serial.println("Could not find a valid BMP185 sensor, check wiring!");
    while (1) {}
  }
}


void loop() {
  float pressure = 0;
  float delta = 0;
  static float previous_pressure = 0;

  for (size_t i = 0; i < 5; i++) {
    pressure += (float)bmp.readSealevelPressure(altitude);
  }
  pressure = pressure / 5;

  if (pressure != 0) {
    Serial.print("Current preassure: ");
    Serial.println(pressure);

    delta = calc_presure_delta(pressure, previous_pressure);
    previous_pressure = pressure;
    byte rain = run_knn(pressure, delta);
    if(rain) {
      digitalWrite(LED_PIN_BLUE, LOW);
      digitalWrite(LED_PIN_WHITE, HIGH);
    } else {
      digitalWrite(LED_PIN_BLUE, HIGH);
      analogWrite(LED_PIN_WHITE, 255 - WHITE_PWN);
    }
    Serial.print("output: ");
    Serial.println(rain);
  }
  delay(MILLISECONDS_30MIN);
}
