/*********************************************************************************************
**  colebrook.cpp
**  Created by Rafael on 11/24/20.				
**  Copyright 2020. Rafael. All rights reserved.	
*********************************************************************************************/

#include <stdio.h>
#include <math.h>

// Constantes do problema
double e = 0.046; // milimetros
double d = 0.25; // Metros
double ro = 998; //
double mi = 0.001; //
double fi = 0.03; // valor inicial para o fator de atrito (0.01-0.08)



// altera a linha do return, pra ser igual a sua fórmula matemática para velocidade
// i.e , atualmente a equação abaixo representa V = raiz quadrada de (204.7/ (24.6 + 80f))
double velocity(double f)
{
    return sqrt(204.7/(24.6 + 80*f));
}

// Não mude nada daqui pra baixo

double reynolds(double v)
{
    return (ro * v * d) / mi;
}

double colebrook(double reynolds)
{
    double rugosidadeRelativa = e/(d*1000);
    int i = 0;
    double A, B, lhs, rhs;
    double friction = fi;
    while (true)
    {
	//printf("Loop %d\n", i);
	double t = sqrt(friction);
	A = rugosidadeRelativa/3.71;
	B = 2.51/(reynolds*t);
	//printf("A = %.10lf\nB = %.10lf\n", A, B);
	
	rhs = -2 * log10(A + B);
	lhs = 1/sqrt(friction);
	
	//printf("LHS = %f\nRHS = %f\nFriction = %f\n", lhs, rhs, friction);

	if (abs(lhs - rhs) <= 0.0001)
	    break;
	friction = friction - 0.000001;
	i++;
    }
    printf("\nFriction = %lf", friction);
    return friction;
}

int main(int argc, char *argv[]) 
{
    // Starting values
    // first we define a velocity function
    double vi = velocity(fi);
    // then we calculate reynods
    double re, friction, vf;

    int i = 0;
    while (true)
    {
	printf("\nLoop %d", i);
	re = reynolds(vi);
	friction = colebrook(re);
	vf = velocity(friction);
	if (abs(vf - vi) <= 0.001)
	    break;
	vi = vf;
	i++;
    }

    // initiating loop
    printf("\nVelocity = %f\n", vf);
    return 0;
}
