尽管可见光和近红外光谱中蕴含了能够反映物质成分和结构信息的吸收特征，但是解析一条复杂的光谱却是非平凡的。最初人们经常使用高斯模型来拟合吸收特征，后来发现它在某些场景中并不适用，于是Sunshine等人基于能量与平均键长之间的能量律关系提出了修正高斯模型（modified Gaussian model, MGM）。MGM在此后便主导了此类光谱解析工作，大量的使用MGM的文献不断涌现。
下面结合热红外光谱分解给出MGM的python应用示例。
首先，读取一条由安捷伦4300实测的岩心波谱，截取其中8800-9600nm区间的光谱片段。
```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
data = pd.read_csv('./2002-12-15T22-11-28.csv')
x = 10000/data['Wavenumber'].values #波长，以μm为单位
y = d['Intensity'].values/100 #反射率
y = y[(x>8.8) & (x<9.6)]
x = x[(x>8.8) & (x<9.6)]*1000 #波长单位转为nm
plt.plot(x, y)
plt.xlabel("$ wavelength /\mu m$")
plt.ylabel("$reflectance$")
```
![image](https://github.com/user-attachments/assets/7ec49cf1-f98f-4ba9-a640-e488904e64de)

然后，执行去除连续统处理。与Tetracorder使用的去除连续统算法略有不同，这里使用著名的凸包算法：
```python
from scipy import interpolate
from scipy.spatial import ConvexHull
def get_continuum_removal(x, y):
    points = np.array([x, y]).T
    points = points[x.argsort()]
    points = np.vstack([np.array([[points[0, 0], -1]]), points, np.array([[points[-1, 0], -1]])])
    hull = ConvexHull(points)
    hull_points_indices = hull.vertices
    hull_points_indices.sort()
    hull = points[hull_points_indices[1:-1]]
    tck = interpolate.splrep((hull[:, 0]), (hull[:, 1]), k=1)
    iy_hull = interpolate.splev(x, tck, der=0)
    norm = y/iy_hull
    return norm
norm = get_continuum_removal(x, y)
data = np.vstack([x, norm]).T
plt.plot(data[:, 0], data[:, 1])
plt.xlabel("$wavelength /n m$")
plt.ylabel("$normalized\ reflectance$")
```
![image](https://github.com/user-attachments/assets/08c91466-2977-4a9f-ba89-3055f80da689)

对去除连续统的光谱执行高斯分解：
```python
points=np.array([9430.15817393, 9299.41032439, 9156.58679071, 8987.87293269])
mstruc, datstruc=init(points)
mstruc, datstruc=process(mstruc, datstruc)
plt.figure(figsize=(8,5),dpi=400)
plt.plot(datstruc['wavel'],(datstruc['ratio'] ))
plt.plot(datstruc['wavel'],(datstruc['fit'] ),'+')
#plt.plot(datstruc['wavel'],(datstruc['cont'] ))
for i in datstruc['gauss'].T:
    plt.plot(datstruc['wavel'],(i))
plt.grid()
plt.xlabel("$ wavelength /n m$")
```

![image](https://github.com/user-attachments/assets/ccf92055-6911-4ea1-af67-c27750e10368)
