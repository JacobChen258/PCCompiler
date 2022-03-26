#include "../starter.c"


int main() {
/***** Main *****/
int_t _t1;
_t1 = 3;
int_t b;
b = _t1;
int_t _t3;
_t3 = 1;
int_t _t4;
_t4 = 2;
int_t _t5;
_t5 = 3;
list_t * _t2 = list_init(3);
list_init_add(int_v,_t2,_t3);
list_init_add(int_v,_t2,_t4);
list_init_add(int_v,_t2,_t5);

int_t _t7;
for (_t7 = 0; _t7 < 3; _t7 += 1){
    i = list_get(int_v, _t2, _t7);
    b = i;
    int_t _t9;
    _t9 = 3;
    int_t a;
    a = _t9;
    str_t _t10;
    _t10 = "a";
    str_t c;
    c = _t10;
}

/***** End of main *****/

/***** Memory clean up *****/
list_free(_t2);

/***** End of Memory clean up *****/

    return 0;
}
