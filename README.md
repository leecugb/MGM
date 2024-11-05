尽管可见光和近红外光谱中蕴含了能够反映物质成分和结构信息的吸收特征，但是解析一条复杂的光谱却是非平凡的。最初人们经常使用高斯模型来拟合吸收特征，后来发现它在某些场景中并不适用，于是Sunshine等人基于能量与平均键长之间的能量律关系提出了修正高斯模型（modified Gaussian model, MGM）。MGM在此后便主导了此类光谱解析工作，大量的使用MGM的文献不断涌现。
下面结合热红外光谱分解给出MGM的python应用示例。

'''python
import pandas as pd
import numpy as np
data = pd.read_csv('./2002-12-15T22-11-28.csv')
x = 10000/data['Wavenumber'].values #波长，以μm为单位
y = d['Intensity'].values/100 #反射率
y = y[(x>8.8) & (x<9.6)]
x = x[(x>8.8) & (x<9.6)]*1000 #波长单位转为nm
plt.plot(x, y)
plt.xlabel("$ wavelength /\mu m$")
plt.ylabel("$reflectance$")
![Uploading image.png…]()
