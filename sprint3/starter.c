#include <stdio.h>
#include <stdlib.h>
#include <stdarg.h>
#include <stdbool.h>

#define NONE_LITERAL 42;

typedef double float_t;
typedef long long int_t;
typedef char char_t;
typedef int bool_t;
typedef int none_t;
typedef struct list list_t;
typedef union data data_t;

struct list
{
  data_t *data;
  int_t length;
  int_t uninitialized_length;
};

union data
{
  int_t int_v;
  float_t float_v;
  char_t char_v;
  bool_t bool_v;
  none_t none_v;
  list_t list_v;
};

list_t *list_init(int_t length)
{
  list_t *list = malloc(sizeof(data_t));
  list->data = malloc(length * sizeof(void *));
  list->length = length;
  list->uninitialized_length = length;
  return list;
}

void list_init_add_internal(list_t *list, data_t value)
{
  if (list->uninitialized_length == 0)
  {
    printf("RUNTIME ERROR: Trying to add more initial elements to full list. Length is %lld\n", list->length);
    exit(1);
  }
  data_t *addr = list->data + list->length - list->uninitialized_length;
  *addr = value;
  list->uninitialized_length--;
}

void list_add_internal(list_t *list, data_t value)
{
  if (list->uninitialized_length != 0)
  {
    printf("RUNTIME ERROR: List initialization is not complete. Length is %lld, uninitialized length is %lld\n", list->length, list->uninitialized_length);
    exit(1);
  }

  list->length++;
  list->data = realloc(list->data, list->length * sizeof(data_t));
  data_t *addr = list->data + list->length - 1;
  *addr = value;
}

void list_free(list_t *list)
{
  if (list == NULL)
    return;
  free(list->data);
  free(list);
}

data_t list_get_internal(list_t *list, int_t index)
{
  if (list->uninitialized_length != 0)
  {
    printf("RUNTIME ERROR: List initialization is not complete. Length is %lld, uninitialized length is %lld\n", list->length, list->uninitialized_length);
    exit(1);
  }
  if (index >= list->length)
  {
    printf("RUNTIME ERROR: Index out of bounds. Trying to access %lld, length is %lld\n", index, list->length);
    exit(1);
  }
  return list->data[index];
}

void input_helper_invalid_input()
{
  int c;
  while ((c = getchar()) != EOF && c != '\n')
    continue;
  if (c == EOF)
  {
    printf("RUNTIME ERROR: Reaching unexpected EOF.\n");
    exit(1);
  }
  printf("Invalid input. Please try again.\n");
}

data_t input_internal(char *prompt, char type)
{
  data_t value;
start:
  printf("%s", prompt);
  switch (type)
  {
  // https://stackoverflow.com/questions/40551037/scanf-not-working-on-invalid-input
  case 'i':
    printf(" (expecting int): ");
    if (scanf("%lld", &value.int_v) != 1)
    {
      input_helper_invalid_input();
      goto start;
    }
    break;
  case 'f':
    printf(" (expecting float): ");
    if (scanf("%lf", &value.float_v) != 1)
    {
      input_helper_invalid_input();
      goto start;
    }
    break;
  case 'c':
    printf(" (expecting char): ");
    if (scanf("%c", &value.char_v) != 1)
    {
      input_helper_invalid_input();
      goto start;
    }
    break;
  case 'b':
    printf(" (expecting bool): ");
    if (scanf("%d", &value.bool_v) != 1)
    {
      input_helper_invalid_input();
      goto start;
    }
    break;
  default:
    printf("RUNTIME ERROR: Unknown type %c\n", type);
    exit(1);
  }

  return value;
}

int print_internal(int items_count, ...)
{
  va_list valist;
  va_start(valist, items_count);

  for (int i = 0; i < items_count; i++)
  {
    char type = va_arg(valist, /* char_t */ int);
    switch (type)
    {
    case 'i':
      printf("%lld", va_arg(valist, int_t));
      break;
    case 'f':
      printf("%lf", va_arg(valist, float_t));
      break;
    case 'c':
      printf("%c", va_arg(valist, /* char_t */ int));
      break;
    case 'b':
      printf("%s", va_arg(valist, bool_t) ? "true" : "false");
      break;
    case 's':
      printf("%s", va_arg(valist, char *));
      break;
    default:
      printf("RUNTIME ERROR: Unknown type: %c\n", type);
      exit(1);
    }
    printf(" ");
  }
  printf("\n");
  va_end(valist);
  return 0;
}

#define list_get(vname, list, index) \
  list_get_internal(list, index).vname

#define list_init_add(vname, list, value) \
  list_init_add_internal(list, (data_t){.vname = value})

#define list_add(vname, list, value) \
  list_add_internal(list, (data_t){.vname = value})

#define input(vname, prompt) \
  input_internal(prompt, #vname[0]).vname

#define print_int(X) \
  (print_internal(1, 'i', X))
