/*********************************************************************************************
**  Engrenagem.cpp
**  Created by Edu on 11/29/21.				
**  Copyright 2021. Edu. All rights reserved.	
*********************************************************************************************/

#include <stdio.h>
#include <math.h>

//--------------------------------------------------------------------------CALCULO DO TORQUE DO MOTOR

double calcula_TORQUE_motor(double Pmotor, double RPMmotor)
{
    double  torquemotor=0;
    torquemotor = (Pmotor*1000/RPMmotor);
    return torquemotor;
}

//--------------------------------------------------------------------------CALCULO DO TORQUE DOS EIXOS

double calcula_TORQUE_eixo2 (int Z1, int Z2, double torquemotor)
{
    double torque2=0;
    torque2 = torquemotor*(Z2/Z1);
    return torque2;
}

double calcula_TORQUE_eixo3 (int Z3, int Z4, double torque2)
{
    double torque3=0;
    torque3 = torque2*Z3/Z4;
    return torque3;
}

//--------------------------------------------------------------------------RPM EIXO 2

double calcula_RPM_eixo2 (int Z1, int Z2, double RPMmotor)
{
    double rotacao2=0;
    rotacao2 = RPMmotor*(Z1/Z2);
    return rotacao2;
}

//--------------------------------------------------------------------------RPM EIXO 3

double calcula_RPM_eixo3 (int Z3, int Z4, double rotacao2)
{
    double rotacao3=0;
    rotacao3 = rotacao2*(Z3/Z4);
    return rotacao3;
}

//--------------------------------------------------------------------------INT MAIN

int main ()
{ 
    double Pmotor=0;
    
        printf("Informe um valor de potencia para o motor em WATTS: ");
        scanf("%lf", &Pmotor);
        //printf("Pmotor= %i\", Pmotor);  
    
    double RPMmotor=0; 
    
        printf("Informe um valor da rotaçao do motor em rad/s: ");
        scanf("%lf", &RPMmotor);
        //printf("\nRPMm = %lf", RPMm);
          
    double torque;
    
        torque= calcula_TORQUE_motor(Pmotor,RPMmotor); 
        printf("\nTorque do motor = %lf\n", torque);

   
    int Z1,Z2,Z3,Z4;
    
        printf("\nNumero de dentes das engrenagens 1: ");
        scanf("%i", &Z1); 
        printf("Numero de dentes das engrenagens 2: ");
        scanf("%i", &Z2);
        printf("Numero de dentes das engrenagens 3: ");
        scanf("%i", &Z3);
        printf("Numero de dentes das engrenagens 4: ");
        scanf("%i", &Z4);

//--------------------------------------------------------------------------MOSTRA AS ROTAÇÕES

    double rotacao2;
    
        rotacao2 = calcula_RPM_eixo2(Z1, Z2, RPMmotor); 
        printf("\nRotacao do eixo 2 = %lf\n", rotacao2);
    
    double rotacao3;
    
        rotacao3= calcula_RPM_eixo3(Z3, Z4, rotacao2); 
        printf("\nRotacao do eixo 3 = %lf\n", rotacao3);

return 0;  
}