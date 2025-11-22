#include "wokwi-api.h"
#include <stdio.h>
#include <stdlib.h>

typedef struct {
  pin_t pin;
  float pressure;
} chip_data_t;

void chip_timer_callback(void *data) 
{
  chip_data_t *chip_data = (chip_data_t*)data;
  float pressure = attr_read(chip_data->pressure);  //read the attribute value with id pressure and assign it to pressure variable
  float volts = 5 * (pressure / 4096.0); //calculating the volts
  pin_dac_write(chip_data->pin, volts);  //return volts to the sensor pin
}

void chip_init() 
{
  chip_data_t *chip_data = (chip_data_t*)malloc(sizeof(chip_data_t));
  chip_data->pressure = attr_init("pressure", 50);  //default value of pressure = 50
  chip_data->pin = pin_init("A0", ANALOG);  //initialize sensor with analog communication

  const timer_config_t config = 
  {
    .callback = chip_timer_callback,
    .user_data = chip_data,
  };

  timer_t timer_id = timer_init(&config);
  timer_start(timer_id, 1000, true);
}

