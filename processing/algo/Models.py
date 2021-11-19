from sqlalchemy.orm import declarative_base, Session, relationship
from sqlalchemy import Column, Integer, String, Float, ForeignKey, select, UniqueConstraint

Base = declarative_base()


class NutrientRun(Base):
    __tablename__ = 'nutrientRun'

    id = Column(Integer, primary_key=True)
    file_name = Column(String)

    samples = relationship("NutrientSamples", backref="nutrientRun")
    file_processed = relationship("NutrientRunProcessed", backref="nutrientRun")
    file_header = relationship("NutrientHeader", backref="nutrientRun")

    baselines = relationship("NutrientBaselines", backref="nutrientRun")
    drifts = relationship("NutrientDrifts", backref="nutrientRun")

    __table_args__ = (UniqueConstraint('file_name'),)


class NutrientSamples(Base):
    __tablename__ = 'nutrientSamples'
    id = Column(Integer, primary_key=True)
    sample_id = Column(String)
    cup_type = Column(String)
    peak_number = Column(Integer)
    dilution = Column(Float)
    time = Column(Float)

    deployment = Column(String)
    rosette_position = Column(String)

    run_number = Column(Integer, ForeignKey('nutrientRun.id'))
    survey_name = Column(Integer, ForeignKey('survey.id'))

    measurements = relationship("NutrientMeasurements", backref="nutrientSamples")

    def __repr__(self):
        return f'Sample({self.sample_id}, peak num{self.peak_number})'

    __table_args__ = (UniqueConstraint('run_number', 'peak_number'),)


class NutrientMeasurements(Base):
    __tablename__ = 'nutrientMeasurements'

    id = Column(Integer, primary_key=True)

    raw_measurement = Column(Float)
    corrected_measurement = Column(Float)
    concentration = Column(Float)
    quality_flag = Column(Integer)

    nutrient_sample = Column(Integer, ForeignKey('nutrientSamples.id'))
    analyte = Column(Integer, ForeignKey('nutrientAnalyte.id'))

    baseline = relationship("NutrientBaselines", backref="nutrientMeasurements")
    drift = relationship("NutrientDrifts", backref="nutrientMeasurements")

    __table_args__ = (UniqueConstraint('nutrient_sample', 'analyte'), )


    def __repr__(self):
        return f'Measurement({self.analyte}, conc{self.concentration})'


class NutrientAnalyte(Base):
    __tablename__ = 'nutrientAnalyte'

    id = Column(Integer, primary_key=True)
    type = Column(String)

    measurements = relationship("NutrientMeasurements", backref="nutrientAnalyte")
    baselines = relationship("NutrientBaselines", backref="nutrientAnalyte")
    drifts = relationship("NutrientDrifts", backref="nutrientAnalyte")

    header = relationship("NutrientHeader", backref="nutrientAnalyte")

    __table_args__ = (UniqueConstraint('type'),)


class Survey(Base):
    __tablename__ = 'survey'

    id = Column(Integer, primary_key=True)
    survey_name = Column(String)
    samples = relationship("NutrientSamples", backref="survey")

    __table_args__ = (UniqueConstraint('survey_name'),)


class NutrientBaselines(Base):
    __tablename__ = 'nutrientBaselines'

    id = Column(Integer, primary_key=True)
    analyte = Column(Integer, ForeignKey('nutrientAnalyte.id'))
    run_number = Column(Integer, ForeignKey('nutrientRun.id'))
    peak_number = Column(Integer)
    measurement = Column(Integer, ForeignKey('nutrientMeasurements.id'))

    __table_args__ = (UniqueConstraint('analyte', 'run_number', 'peak_number'),)


class NutrientDrifts(Base):
    __tablename__ = 'nutrientDrifts'

    id = Column(Integer, primary_key=True)
    analyte = Column(Integer, ForeignKey('nutrientAnalyte.id'))
    run_number = Column(Integer, ForeignKey('nutrientRun.id'))
    peak_number = Column(Integer)
    measurement = Column(Integer, ForeignKey('nutrientMeasurements.id'))

    __table_args__ = (UniqueConstraint('analyte', 'run_number', 'peak_number'),)


class NutrientRunProcessed(Base):
    __tablename__ = 'nutrientRunProcessed'

    id = Column(Integer, primary_key=True)
    time_last_modified = Column(Float)

    run_number = Column(Integer, ForeignKey('nutrientRun.id'))

    __table_args__ = (UniqueConstraint('run_number'),)


class NutrientHeader(Base):
    __tablename__ = 'nutrientHeader'

    id = Column(Integer, primary_key=True)
    analyte = Column(Integer, ForeignKey('nutrientAnalyte.id'))
    run_number = Column(Integer, ForeignKey('nutrientRun.id'))
    channel = Column(Integer)

    gain = Column(Integer)
    baseline_offset = Column(Integer)
    carryover_coefficient = Column(Float)
    cal_zero_mean_ad = Column(Float)
    cal_coefficient_one = Column(Float)
    cal_coefficient_two = Column(Float)

    __table_args__ = (UniqueConstraint('analyte', 'run_number'),)
