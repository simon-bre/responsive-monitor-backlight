#define R 9
#define G 10
#define B 11

void setRGB(int r, int g, int b){
  analogWrite(R,r);
  analogWrite(G,g);
  analogWrite(B,b);
}

byte RedLight;
byte GreenLight;
byte BlueLight;

void setLedColorHSV(byte h, byte s, byte v) {
  // this is the algorithm to convert from RGB to HSV
  h = (h * 192) / 256;  // 0..191
  unsigned int i = h / 32;   // We want a value of 0 thru 5
  unsigned int f = (h % 32) * 8;   // 'fractional' part of 'i' 0..248 in jumps

  unsigned int sInv = 255 - s;  // 0 -> 0xff, 0xff -> 0
  unsigned int fInv = 255 - f;  // 0 -> 0xff, 0xff -> 0
  byte pv = v * sInv / 256;  // pv will be in range 0 - 255
  byte qv = v * (256 - s * f / 256) / 256;
  byte tv = v * (256 - s * fInv / 256) / 256;

  switch (i) {
  case 0:
    RedLight = v;
    GreenLight = tv;
    BlueLight = pv;
    break;
  case 1:
    RedLight = qv;
    GreenLight = v;
    BlueLight = pv;
    break;
  case 2:
    RedLight = pv;
    GreenLight = v;
    BlueLight = tv;
    break;
  case 3:
    RedLight = pv;
    GreenLight = qv;
    BlueLight = v;
    break;
  case 4:
    RedLight = tv;
    GreenLight = pv;
    BlueLight = v;
    break;
  case 5:
    RedLight = v;
    GreenLight = pv;
    BlueLight = qv;
    break;
  }
}

void setup() {
  setRGB(0,0,0);
  Serial.begin(9600);
}

//main loop
bool colorcycle = false;
int h = 0;
char colors[3];
int idx = 0;
void loop() {
  if(colorcycle){
    h = (h+1) % 255;
    setLedColorHSV(h, 255, 255);
    setRGB(RedLight,GreenLight,BlueLight);
    delay(50);
  }
  else{
    while (Serial.available()>0) {
      colors[idx] = Serial.read();
      idx++;
      if(idx>2){
        idx = 0;
        setRGB(colors[0],colors[1],colors[2]);
      }
    }
    delay(1);
  }
}
