from flask import Flask, render_template, request, send_file
import pandas as pd
import matplotlib.pyplot as plt
import os
import uuid
import seaborn as sns


app = Flask(__name__)
GRAPH_FOLDER = 'static/graphs'
OUTPUT_FOLDER = 'static/output'
os.makedirs(GRAPH_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # 🟡 File Upload or Manual Entry
        if 'csv_file' in request.files and request.files['csv_file'].filename != '':
            csv_file = request.files['csv_file']
            df = pd.read_csv(csv_file)
            df.columns = df.columns.str.strip().str.capitalize()   # 🧼 Clean column names
            print("🧾 CSV Columns:", df.columns.tolist())          # 🕵️ Debug print

        else:
            names = request.form.getlist('name')
            math = request.form.getlist('math')
            physics = request.form.getlist('physics')
            chemistry = request.form.getlist('chemistry')
            english = request.form.getlist('english')
            computer = request.form.getlist('computer')

            data = []
            for i in range(len(names)):
                data.append({
                    'StudentID': i + 1,
                    'Name': names[i],
                    'Math': int(math[i]),
                    'Physics': int(physics[i]),
                    'Chemistry': int(chemistry[i]),
                    'English': int(english[i]),
                    'Computer': int(computer[i])
                })
            df = pd.DataFrame(data)

        # 🧮 Analysis
        subjects = ['Math', 'Physics', 'Chemistry', 'English', 'Computer']
        df['Total'] = df[subjects].sum(axis=1)
        df['Average'] = df[subjects].mean(axis=1)

        # 🎓 Auto Grading System
        def grade(avg):
            if avg >= 90: return 'A+'
            elif avg >= 80: return 'A'
            elif avg >= 70: return 'B'
            elif avg >= 60: return 'C'
            elif avg >= 40: return 'D'
            else: return 'F'
        df['Grade'] = df['Average'].apply(grade)

        # ✅ Pass / Fail Counter
        passed = len(df[df['Average'] >= 40])
        failed = len(df[df['Average'] < 40])

        # 🧠 Key Insights
        top_scorer = df.loc[df['Total'].idxmax()]['Name']
        bottom_scorer = df.loc[df['Total'].idxmin()]['Name']
        class_avg = round(df['Total'].mean(), 2)
        subject_avg = df[subjects].mean().to_dict()
        hardest_subject = min(subject_avg, key=subject_avg.get)
        easiest_subject = max(subject_avg, key=subject_avg.get)

        # 💾 Save analyzed CSV
        analyzed_path = os.path.join(OUTPUT_FOLDER, f'analyzed_{uuid.uuid4().hex}.csv')
        df.to_csv(analyzed_path, index=False)

        # 📊 1️⃣ Bar Chart - Total Marks per Student
        plt.figure(figsize=(10, 5))
        plt.bar(df['Name'], df['Total'], color='skyblue')
        plt.xlabel('Student'); plt.ylabel('Total Marks'); plt.title('Total Marks per Student')
        plt.xticks(rotation=45)
        bar_chart = os.path.join(GRAPH_FOLDER, f'bar_{uuid.uuid4().hex}.png')
        plt.tight_layout(); plt.savefig(bar_chart); plt.close()

        # 📈 2️⃣ Line Chart - Marks Trend per Student
        plt.figure(figsize=(10, 5))
        for idx, row in df.iterrows():
            plt.plot(subjects, row[subjects], marker='o', label=row['Name'])
        plt.xlabel('Subjects'); plt.ylabel('Marks'); plt.title('Marks Trend per Student')
        plt.legend(fontsize=8)
        line_chart = os.path.join(GRAPH_FOLDER, f'line_{uuid.uuid4().hex}.png')
        plt.tight_layout(); plt.savefig(line_chart); plt.close()

        # 🥧 3️⃣ Pie Chart - Subject Average Contribution
        plt.figure(figsize=(6, 6))
        plt.pie(subject_avg.values(), labels=subject_avg.keys(), autopct='%1.1f%%', startangle=140)
        plt.title('Subject-wise Average Contribution')
        pie_chart = os.path.join(GRAPH_FOLDER, f'pie_{uuid.uuid4().hex}.png')
        plt.tight_layout(); plt.savefig(pie_chart); plt.close()

        # 📊 4️⃣ Histogram - Marks Distribution
        plt.figure(figsize=(8, 4))
        plt.hist(df['Total'], bins=5, color='orange', edgecolor='black')
        plt.title('Marks Distribution'); plt.xlabel('Total Marks'); plt.ylabel('Number of Students')
        hist_chart = os.path.join(GRAPH_FOLDER, f'hist_{uuid.uuid4().hex}.png')
        plt.tight_layout(); plt.savefig(hist_chart); plt.close()

        # 📦 5️⃣ Box Plot - Subject Variations
        plt.figure(figsize=(8, 5))
        df[subjects].plot.box()
        plt.title('Subject-wise Marks Variation')
        box_chart = os.path.join(GRAPH_FOLDER, f'box_{uuid.uuid4().hex}.png')
        plt.tight_layout(); plt.savefig(box_chart); plt.close()

        # 🔥 6️⃣ Heatmap - Subject Correlation
        plt.figure(figsize=(6, 5))
        sns.heatmap(df[subjects].corr(), annot=True, cmap='coolwarm')
        plt.title('Subject Correlation Heatmap')
        heat_chart = os.path.join(GRAPH_FOLDER, f'heat_{uuid.uuid4().hex}.png')
        plt.tight_layout(); plt.savefig(heat_chart); plt.close()

        # 🔁 Return Dashboard
        return render_template(
            'dashboard.html',
            tables=[df.to_html(classes='data table table-striped', index=False)],
            top_scorer=top_scorer,
            bottom_scorer=bottom_scorer,
            class_avg=class_avg,
            subject_avg=subject_avg,
            hardest_subject=hardest_subject,
            easiest_subject=easiest_subject,
            passed=passed, failed=failed,
            bar_chart=bar_chart, pie_chart=pie_chart, line_chart=line_chart,
            hist_chart=hist_chart, box_chart=box_chart, heat_chart=heat_chart,
            analyzed_path=analyzed_path
        )
    return render_template('index.html')


@app.route('/download/<path:filename>')
def download(filename):
    return send_file(filename, as_attachment=True)

@app.route('/how-it-works')
def how_it_works():
    return render_template('how_it_works.html')



# ✅ Run App
if __name__ == '__main__':
    app.run(debug=True)





